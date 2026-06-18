import os
import sys
import io
import pickle
import threading
from functools import lru_cache
from datetime import datetime
from typing import Literal
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
ML_ENGINE_PATH = os.path.join(PROJECT_ROOT, "ml_engine")

ML_ENGINE_URL = os.environ.get("ML_ENGINE_URL")

# Dynamically import ML classes only if running locally (no ML_ENGINE_URL proxy config)
DataProcessor = None
PortfolioClusterer = None
TrendPredictor = None
TaxBacktester = None

if not ML_ENGINE_URL:
    if ML_ENGINE_PATH not in sys.path:
        sys.path.insert(0, ML_ENGINE_PATH)
    try:
        from src import DataProcessor, PortfolioClusterer, TrendPredictor, TaxBacktester
    except ImportError as e:
        print(f"[Warning] Failed to import local ML engine: {e}. Local ML execution will not be available.")

from app import store
from app.schemas import (
    ChartPoint,
    DashboardSummary,
    Opportunity,
    SettingsUpdate,
    Trade,
    UserSettings,
    HarvestRequest,
)

app = FastAPI(
    title="Tax-Loss Harvesting API",
    version="0.1.0",
    description="Backend API for the Tax-Loss Harvesting dashboard.",
)

allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if os.environ.get("ALLOWED_ORIGINS"):
    allowed_origins.extend(os.environ.get("ALLOWED_ORIGINS").split(","))
else:
    # Safely allow any origin in development/deployment if not specified
    allowed_origins.append("*")

# If wildcard is used, allow_credentials must be False to comply with CORS standards
allow_credentials = "*" not in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared ML instances loaded on startup
CLUSTER_MODEL_PATH = "models/clusterer.pkl"
PREDICTOR_MODEL_PATH = "models/predictor.pkl"
GLOBAL_UNIVERSE = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "TSLA",
    "JPM",
    "V",
    "PG",
    "KO",
    "PEP",
]

cluster_engine = None
predictor = None
data_pipeline = None


def load_or_train_models():
    global cluster_engine, predictor, data_pipeline

    if ML_ENGINE_URL:
        print("[ML Engine] Running in proxy mode (ML_ENGINE_URL is set). Local model loading/training bypassed.")
        return

    if DataProcessor is None:
        print("[ML Engine] Local ML engine modules are missing. Bypassing local model loading/training.")
        return

    os.makedirs("models", exist_ok=True)
    data_pipeline = DataProcessor(
        GLOBAL_UNIVERSE,
        start_date="2021-01-01",
        end_date=datetime.now().strftime("%Y-%m-%d"),
    )

    if os.path.exists(CLUSTER_MODEL_PATH) and os.path.exists(PREDICTOR_MODEL_PATH):
        print("[ML Engine] Loading Pre-trained ML Engine Models from Disk...")
        try:
            with open(CLUSTER_MODEL_PATH, "rb") as file:
                cluster_engine = pickle.load(file)
            with open(PREDICTOR_MODEL_PATH, "rb") as file:
                predictor = pickle.load(file)
        except Exception as e:
            print(f"[Warning] Error loading pickles: {e}. Retraining...")
            cluster_engine = None
            predictor = None

    if cluster_engine is None or predictor is None:
        print(
            "[ML Engine] Pre-trained binary model files missing or invalid. Training on-the-fly..."
        )
        try:
            # 1. Download data
            data_pipeline.download_data()

            # 2. Train and save cluster model
            cluster_engine = PortfolioClusterer(n_clusters=3)
            cluster_engine.fit_clusters(data_pipeline)
            with open(CLUSTER_MODEL_PATH, "wb") as file:
                pickle.dump(cluster_engine, file)
            print(f"[Success] Saved clusterer: {CLUSTER_MODEL_PATH}")

            # 3. Train and save trend predictor model
            predictor = TrendPredictor()
            predictor.train_model(data_pipeline, "AAPL")
            with open(PREDICTOR_MODEL_PATH, "wb") as file:
                pickle.dump(predictor, file)
            print(f"[Success] Saved predictor: {PREDICTOR_MODEL_PATH}")
        except Exception as e:
            print(f"[Error] Error training models on the fly: {e}")

    print("[ML Engine] Models loaded and ready.")


@lru_cache(maxsize=128)
def get_cached_backtest(initial_capital: float, tax_rate: float):
    if TaxBacktester is None:
        raise RuntimeError("Local ML Engine is not available (TaxBacktester is None). Please configure ML_ENGINE_URL.")
    print(
        f"[Backtest] Running historical backtest simulation (Capital={initial_capital}, TaxRate={tax_rate})..."
    )
    backtester = TaxBacktester(initial_capital=initial_capital, tax_rate=tax_rate)
    # Run simulation on GLOBAL_UNIVERSE
    history_df = backtester.run_simulation(GLOBAL_UNIVERSE, "2022-01-01", "2025-12-31")

    chart_data = []
    for date, row in history_df.iterrows():
        chart_data.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "baseline_value": round(row["Baseline_Value"], 2),
                "active_value": round(row["Active_Engine_Value"], 2),
                "tax_savings_cumulative": round(row["Cumulative_Tax_Savings"], 2),
            }
        )

    result = {
        "summary": {
            "initial_capital": initial_capital,
            "final_baseline_value": round(history_df["Baseline_Value"].iloc[-1], 2),
            "final_active_value": round(history_df["Active_Engine_Value"].iloc[-1], 2),
            "total_tax_saved": round(history_df["Cumulative_Tax_Savings"].iloc[-1], 2),
            "strategy_tax_alpha_pct": round(
                (
                    (
                        history_df["Active_Engine_Value"].iloc[-1]
                        - history_df["Baseline_Value"].iloc[-1]
                    )
                    / initial_capital
                )
                * 100,
                2,
            ),
        },
        "time_series_chart_data": chart_data,
    }
    print("[Backtest] Backtest simulation cached successfully.")
    return result


@app.on_event("startup")
def startup_event():
    # Load or train ML models
    load_or_train_models()

    # Pre-warm the backtest cache in a background thread to make the first page load instant
    if not ML_ENGINE_URL and TaxBacktester is not None:
        print("[Cache] Pre-warming backtest simulation cache...")
        threading.Thread(
            target=get_cached_backtest, args=(100000.0, 0.15), daemon=True
        ).start()


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "Tax-Loss Harvesting Backend API",
        "docs": "/docs"
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/dashboard", response_model=DashboardSummary)
def dashboard() -> dict:
    return store.get_dashboard_summary()


@app.get("/api/v1/trades", response_model=list[Trade])
def trades(
    search: str | None = Query(default=None, description="Ticker text to search"),
    status: Literal["Completed", "Pending"] | None = Query(default=None),
) -> list[dict]:
    return store.get_trades(search=search, status=status)


@app.get("/api/v1/tax-alpha", response_model=list[ChartPoint])
def tax_alpha(timeframe: Literal["1Y", "5Y"] = "5Y") -> list[dict]:
    return store.TAX_ALPHA[timeframe]


@app.get("/api/v1/opportunities", response_model=list[Opportunity])
def opportunities() -> list[dict]:
    return store.OPPORTUNITIES


@app.get("/api/v1/settings", response_model=UserSettings)
def settings() -> dict:
    return store.SETTINGS


@app.patch("/api/v1/settings", response_model=UserSettings)
def update_settings(payload: SettingsUpdate) -> dict:
    updates = payload.model_dump(by_alias=True, exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No settings were provided.")

    store.SETTINGS.update(updates)
    return store.SETTINGS


@app.post("/api/v1/recommend")
def recommend_harvest_actions(request: HarvestRequest):
    global cluster_engine, predictor, data_pipeline

    if ML_ENGINE_URL:
        try:
            import httpx
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    f"{ML_ENGINE_URL.rstrip('/')}/api/v1/recommend",
                    json=request.model_dump()
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Error communicating with Render ML Engine: {str(e)}"
            )

    if cluster_engine is None or predictor is None or data_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="ML Models are still loading. Please try again in a few seconds.",
        )

    recommendations = []

    # Lazily ensure underlying historical frames are active
    if data_pipeline.raw_data is None:
        data_pipeline.download_data()

    for asset in request.portfolio:
        ticker = asset.ticker.upper()

        # Verify if the asset exists within our data universe framework
        if ticker not in data_pipeline.raw_data.columns:
            continue

        # Calculate localized unrealized asset loss position
        current_loss = (
            asset.current_price - asset.purchase_price
        ) / asset.purchase_price

        # 1. Evaluate Trend Predictor: Forecast 30-day directional vector
        try:
            predicted_return = predictor.predict_next_30d_move(data_pipeline, ticker)
        except Exception:
            predicted_return = 0.01  # Safe localized statistical baseline fallback

        # 2. Evaluate Rule Engine Action Constraints
        action_signal = predictor.generate_harvest_signal(
            current_loss, predicted_return
        )

        # 3. Matchmaker Action: Pull substitutes if asset meets harvesting criteria
        substitutes = []
        if action_signal == "HARVEST_NOW":
            substitutes = cluster_engine.get_substitutes(ticker)

        recommendations.append(
            {
                "ticker": ticker,
                "current_loss_pct": round(current_loss * 100, 2),
                "predicted_30d_return_pct": round(predicted_return * 100, 2),
                "recommended_action": action_signal,
                "suggested_substitutes": substitutes[
                    :2
                ],  # Limit payload to top 2 alternatives
            }
        )

    return {"processed_at": datetime.now().isoformat(), "results": recommendations}


@app.get("/api/v1/backtest")
def run_historical_backtest(initial_capital: float = 100000.0, tax_rate: float = 0.15):
    if ML_ENGINE_URL:
        try:
            import httpx
            with httpx.Client(timeout=60.0) as client:
                resp = client.get(
                    f"{ML_ENGINE_URL.rstrip('/')}/api/v1/backtest",
                    params={"initial_capital": initial_capital, "tax_rate": tax_rate}
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Error communicating with Render ML Engine: {str(e)}"
            )

    try:
        # Fetch from the cache
        return get_cached_backtest(initial_capital, tax_rate)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simulation processing track encountered a failure: {str(e)}",
        )

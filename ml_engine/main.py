import os
import pickle
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

# Import the core structural blocks directly via our package structure
from src import DataProcessor, PortfolioClusterer, TrendPredictor, TaxBacktester

app = FastAPI(
    title="Portfolio Rebalancer: AI Tax-Loss Harvesting Engine",
    description="Production-ready API endpoints serving risk clustering, price forecasting, and performance analytics.",
    version="2.0.0"
)

# --- 1. Define Request Data Structures (Pydantic Models) ---

class PortfolioAsset(BaseModel):
    ticker: str = Field(..., example="AAPL")
    purchase_price: float = Field(..., description="The price at which the investor bought the stock", example=190.0)
    current_price: float = Field(..., description="The current market price of the asset", example=161.5)

class HarvestRequest(BaseModel):
    portfolio: List[PortfolioAsset]


# --- 2. Shared Engine Initialization (Instant Binary Loading) ---

CLUSTER_MODEL_PATH = "models/clusterer.pkl"
PREDICTOR_MODEL_PATH = "models/predictor.pkl"

# Global fallback parameters for real-time asset validation calculations
GLOBAL_UNIVERSE = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'JPM', 'V', 'PG', 'KO', 'PEP']
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(CURRENT_DIR, "data")
data_pipeline = DataProcessor(GLOBAL_UNIVERSE, start_date="2021-01-01", end_date=datetime.now().strftime("%Y-%m-%d"), dataset_path=DATASET_PATH)

# Structural verification check to ensure models have been generated
if not os.path.exists(CLUSTER_MODEL_PATH) or not os.path.exists(PREDICTOR_MODEL_PATH):
    raise FileNotFoundError(
        "❌ Pre-trained binary model files missing in 'models/'. "
        "Please run 'python save_models.py' first to generate them before starting the API server."
    )

print("⚙️ Loading Pre-trained ML Engine Models from Disk...")
with open(CLUSTER_MODEL_PATH, "rb") as file:
    cluster_engine = pickle.load(file)

with open(PREDICTOR_MODEL_PATH, "rb") as file:
    predictor = pickle.load(file)
print("🚀 Models loaded successfully! FastAPI Engine Ready for Web Traffic.")


# --- 3. API Endpoints ---

@app.get("/")
def read_root():
    return {
        "status": "healthy", 
        "engine": "Tax-Loss Harvesting ML Engine v2.0",
        "mode": "Production (Pickle Serialization Activated)"
    }


@app.post("/api/v1/recommend")
def recommend_harvest_actions(request: HarvestRequest):
    """
    Scans an uploaded user portfolio structure, targets assets experiencing losses, 
    calculates forward risk trajectories, and matches them to cluster-peer substitutes.
    """
    recommendations = []
    
    # Lazily ensure underlying historical frames are active for technical indicators
    if data_pipeline.raw_data is None:
        data_pipeline.download_data()
    
    for asset in request.portfolio:
        ticker = asset.ticker.upper()
        
        # Verify if the asset exists within our data universe framework
        if ticker not in data_pipeline.raw_data.columns:
            continue
            
        # Calculate localized unrealized asset loss position
        current_loss = (asset.current_price - asset.purchase_price) / asset.purchase_price
        
        # 1. Evaluate Trend Predictor: Forecast 30-day directional vector
        try:
            predicted_return = predictor.predict_next_30d_move(data_pipeline, ticker)
        except Exception:
            predicted_return = 0.01  # Safe localized statistical baseline fallback
            
        # 2. Evaluate Rule Engine Action Constraints
        action_signal = predictor.generate_harvest_signal(current_loss, predicted_return)
        
        # 3. Matchmaker Action: Pull substitutes if asset meets harvesting criteria
        substitutes = []
        if action_signal == "HARVEST_NOW":
            substitutes = cluster_engine.get_substitutes(ticker)
            
        recommendations.append({
            "ticker": ticker,
            "current_loss_pct": round(current_loss * 100, 2),
            "predicted_30d_return_pct": round(predicted_return * 100, 2),
            "recommended_action": action_signal,
            "suggested_substitutes": substitutes[:2]  # Limit output payload to top 2 alternatives
        })
        
    return {"processed_at": datetime.now().isoformat(), "results": recommendations}


@app.get("/api/v1/backtest")
def run_historical_backtest(initial_capital: float = 100000.0, tax_rate: float = 0.15):
    """
    Triggers historical simulation engines across macro intervals, compiling 
    chronological time-series arrays engineered specifically for UI integration components.
    """
    try:
        backtester = TaxBacktester(initial_capital=initial_capital, tax_rate=tax_rate)
        # Run historical backtest over static macro tracking interval
        history_df = backtester.run_simulation(GLOBAL_UNIVERSE, "2022-01-01", "2025-12-31")
        
        chart_data = []
        for date, row in history_df.iterrows():
            chart_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "baseline_value": round(row['Baseline_Value'], 2),
                "active_value": round(row['Active_Engine_Value'], 2),
                "tax_savings_cumulative": round(row['Cumulative_Tax_Savings'], 2)
            })
            
        return {
            "summary": {
                "initial_capital": initial_capital,
                "final_baseline_value": round(history_df['Baseline_Value'].iloc[-1], 2),
                "final_active_value": round(history_df['Active_Engine_Value'].iloc[-1], 2),
                "total_tax_saved": round(history_df['Cumulative_Tax_Savings'].iloc[-1], 2),
                "strategy_tax_alpha_pct": round(((history_df['Active_Engine_Value'].iloc[-1] - history_df['Baseline_Value'].iloc[-1]) / initial_capital) * 100, 2)
            },
            "time_series_chart_data": chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation processing track encountered a failure: {str(e)}")


# Execution driver configuration mapping module execution contexts
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
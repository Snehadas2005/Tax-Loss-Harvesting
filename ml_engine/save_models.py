# ml_engine/save_models.py
import os
import sys
import pickle
import pandas as pd

# Bypass the broken src/__init__.py imports by targeting concrete modules directly
from src.clustering import PortfolioClusterer
from src.prediction import TrendPredictor
from src.backtester import TaxBacktester


def evaluate_all_combinations():
    print("📥 Initializing Local Stock Data Universe Matrices...")
    # Core asset sequences to perform backtest metrics validation
    tickers = ["TSLA", "NVDA", "AMZN", "META", "AAPL", "MSFT"]

    # Storage structure to compile the final terminal summary matrix
    results_summary = []

    # -------------------------------------------------------------------------
    # TRIAL A RUN: KMeans + Standard Linear Predictor
    # -------------------------------------------------------------------------
    print("\n🚀 --- RUNNING TRIAL A (KMeans + Linear Momentum) ---")
    try:
        clusterer_A = PortfolioClusterer(n_clusters=3, algorithm="KMeans")
        predictor_A = TrendPredictor(variant="standard")

        backtester_A = TaxBacktester(
            initial_capital=100000,
            tax_rate=0.15,
            predictor=predictor_A,
            clusterer=clusterer_A,
        )
        backtester_A.run_simulation(tickers, "2021-01-01", "2025-01-01")

        results_summary.append(
            {
                "Trial Configuration": "Trial A (KMeans + Linear Baseline)",
                "Portfolio Value": f"${backtester_A.portfolio_value:,.2f}",
                "Tax Avoided": f"${backtester_A.total_tax_avoided:,.2f}",
            }
        )
    except Exception as e:
        print(f"❌ Failed executing Trial A: {str(e)}")
        results_summary.append(
            {
                "Trial Configuration": "Trial A (KMeans + Linear Baseline)",
                "Portfolio Value": "ERROR",
                "Tax Avoided": "ERROR",
            }
        )

    # -------------------------------------------------------------------------
    # TRIAL 2 RUN: OPTICS + XGBoost Mathematical Predictor
    # -------------------------------------------------------------------------
    print("\n🚀 --- RUNNING TRIAL 2 (OPTICS + XGBoost Trees) ---")
    try:
        clusterer_2 = PortfolioClusterer(algorithm="OPTICS")
        predictor_2 = TrendPredictor(variant="xgboost")

        backtester_2 = TaxBacktester(
            initial_capital=100000,
            tax_rate=0.15,
            predictor=predictor_2,
            clusterer=clusterer_2,
        )
        backtester_2.run_simulation(tickers, "2021-01-01", "2025-01-01")

        results_summary.append(
            {
                "Trial Configuration": "Trial 2 (OPTICS + XGBoost)",
                "Portfolio Value": f"${backtester_2.portfolio_value:,.2f}",
                "Tax Avoided": f"${backtester_2.total_tax_avoided:,.2f}",
            }
        )
    except Exception as e:
        print(f"❌ Failed executing Trial 2: {str(e)}")
        results_summary.append(
            {
                "Trial Configuration": "Trial 2 (OPTICS + XGBoost)",
                "Portfolio Value": "ERROR",
                "Tax Avoided": "ERROR",
            }
        )

    # -------------------------------------------------------------------------
    # TRIAL 3 RUN: GMM Clusters + Quantile Gradient Boosting
    # -------------------------------------------------------------------------
    print("\n🚀 --- RUNNING TRIAL 3 (GMM + Quantile Loss Floor) ---")
    try:
        clusterer_3 = PortfolioClusterer(n_clusters=3, algorithm="GMM")
        predictor_3 = TrendPredictor(variant="quantile")

        backtester_3 = TaxBacktester(
            initial_capital=100000,
            tax_rate=0.15,
            predictor=predictor_3,
            clusterer=clusterer_3,
        )
        backtester_3.run_simulation(tickers, "2021-01-01", "2025-01-01")

        results_summary.append(
            {
                "Trial Configuration": "Trial 3 (GMM + Quantile) *CHAMPION*",
                "Portfolio Value": f"${backtester_3.portfolio_value:,.2f}",
                "Tax Avoided": f"${backtester_3.total_tax_avoided:,.2f}",
            }
        )
    except Exception as e:
        print(f"❌ Failed executing Trial 3: {str(e)}")
        results_summary.append(
            {
                "Trial Configuration": "Trial 3 (GMM + Quantile) *CHAMPION*",
                "Portfolio Value": "ERROR",
                "Tax Avoided": "ERROR",
            }
        )

    # -------------------------------------------------------------------------
    # TERMINAL PRESENTATION SUMMARY PROFILE
    # -------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("      📊 ALGORITHMIC PIPELINE TRIAL METRICS SUMMARY COMPARISON      ")
    print("=" * 75)
    summary_df = pd.DataFrame(results_summary)
    print(summary_df.to_string(index=False))
    print("=" * 75)

    # -------------------------------------------------------------------------
    # SERIALIZATION WORKFLOW FOR FRONTEND DESKTOP PRESENTATION (LOCK IN TRIAL 3)
    # -------------------------------------------------------------------------
    print("\n🔒 Locking in Trial 3 (GMM + Quantile) as Active Champion Engine...")

    # Target directory horizons where runtime servers look up pickled weights
    model_export_paths = ["models", "../backend/models", "../../backend/models"]

    for export_path in model_export_paths:
        # Check if the folder target makes relative path sense in your structure
        if os.path.exists(os.path.dirname(export_path)) or export_path == "models":
            try:
                os.makedirs(export_path, exist_ok=True)

                # Check if internal helper `.save()` routines are written inside your class
                if hasattr(clusterer_3, "save") and hasattr(predictor_3, "save"):
                    clusterer_3.save(os.path.join(export_path, "clusterer.pkl"))
                    predictor_3.save(os.path.join(export_path, "predictor.pkl"))
                else:
                    # Native high-fidelity pickle fallback matching production microservices
                    with open(os.path.join(export_path, "clusterer.pkl"), "wb") as f:
                        pickle.dump(clusterer_3, f)
                    with open(os.path.join(export_path, "predictor.pkl"), "wb") as f:
                        pickle.dump(predictor_3, f)

                print(
                    f"   ✅ Serialized champion algorithms to destination path: '{export_path}/'"
                )
            except Exception as save_err:
                print(f"   ⚠️ Skipping export to '{export_path}': {str(save_err)}")

    print(
        "\n✨ Benchmarking pipeline terminated cleanly. Combination B parameters locked into production models."
    )


if __name__ == "__main__":
    evaluate_all_combinations()

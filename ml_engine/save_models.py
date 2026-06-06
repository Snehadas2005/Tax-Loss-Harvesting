import os
import kagglehub
from src.processor import DataProcessor
from src.clustering import PortfolioClusterer
from src.prediction import TrendPredictor
from src.models import ModelArena


def execute_combination_one():
    print("🚀 --- COMMENCING COMBINATION 1 TRIAL --- 🚀")
    path = kagglehub.dataset_download("rohanrao/nifty50-stock-market-data")

    tickers = ["INFY", "TCS", "RELIANCE", "HDFCBANK", "ICICIBANK", "ITC", "SBIN"]
    processor = DataProcessor(
        path, tickers, start_date="2016-01-01", end_date="2021-12-31"
    )
    processor.download_data()

    # Run Regressor Arena Check
    blueprint = TrendPredictor()
    X, y = blueprint._prepare_data(processor.raw_data["INFY"], is_training=True)

    arena = ModelArena()
    champ_name, logs = arena.walk_forward_validation(X, y)

    # Run Cluster Option A (KMeans)
    clusterer_k = PortfolioClusterer(n_clusters=3, algorithm="KMeans")
    clusterer_k.fit_clusters(processor)

    # Run Cluster Option B (Hierarchical)
    clusterer_h = PortfolioClusterer(n_clusters=3, algorithm="Hierarchical")
    clusterer_h.fit_clusters(processor)

    print("\n📝 EXPERIMENT NOTEBOOK DETAILS:")
    print(f"1. Record the Mean Directional Accuracy and RMSE metrics printed above.")
    print(
        f"2. Toggle 'algorithm' inside clustering configurations to note variations in risk twin sets."
    )


if __name__ == "__main__":
    execute_combination_one()

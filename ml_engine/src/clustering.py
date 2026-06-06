import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from src.processor import DataProcessor
from sklearn.cluster import KMeans, AgglomerativeClustering


class PortfolioClusterer:
    def __init__(self, n_clusters=3, algorithm="KMeans"):
        self.n_clusters = n_clusters
        self.algorithm = algorithm
        self.scaler = StandardScaler()
        self.model = None
        self.cluster_map = {}

    def fit_clusters(self, processor):
        """Computes risk features and runs the selected clustering algorithm."""
        if processor.raw_data is None:
            processor.download_data()

        # Calculate features (Returns and Volatility)
        returns = processor.raw_data.pct_change().mean() * 252
        volatility = processor.raw_data.pct_change().std() * (252**0.5)

        features_df = pd.DataFrame(
            {"Returns": returns, "Volatility": volatility}
        ).fillna(0)
        scaled_features = self.scaler.fit_transform(features_df)

        # Select Algorithm Combination
        if self.algorithm == "KMeans":
            self.model = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        elif self.algorithm == "Hierarchical":
            self.model = AgglomerativeClustering(n_clusters=self.n_clusters)

        labels = self.model.fit_predict(scaled_features)
        features_df["Cluster"] = labels

        # Map tickers to alternatives
        self.cluster_map = features_df["Cluster"].to_dict()
        print(f"✅ {self.algorithm} Clustering Completed. Asset Profiles mapped.")
        return features_df

    def get_substitutes(self, ticker):
        target_cluster = self.cluster_map.get(ticker)
        return [
            t
            for t, c in self.cluster_map.items()
            if c == target_cluster and t != ticker
        ]


# Verification Test Block
if __name__ == "__main__":
    print("🚀 Initializing Cluster Engine Test...")

    # 1. Define a diversified test universe
    test_universe = ["AAPL", "MSFT", "GOOGL", "AMZN", "JPM", "V", "PG", "KO", "PEP"]

    # 2. Initialize our structural pipeline components
    data_pipeline = DataProcessor(
        test_universe, start_date="2021-01-01", end_date="2026-01-01"
    )
    cluster_engine = PortfolioClusterer(n_clusters=3)

    # 3. Execute clustering computation
    assigned_clusters = cluster_engine.fit_clusters(data_pipeline)
    print("\n📊 Generated Cluster Mapping:")
    print(assigned_clusters[["Cluster"]].to_string())

    # 4. Query a substitute candidate
    test_target = "AAPL"
    recommendations = cluster_engine.get_substitutes(test_target)
    print(f"\n🔄 Risk-Parity Twin Substitutes for '{test_target}': {recommendations}")

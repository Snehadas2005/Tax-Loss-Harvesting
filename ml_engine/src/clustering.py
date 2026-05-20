import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from src.processor import DataProcessor

class PortfolioClusterer:
    def __init__(self, n_clusters=3):
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.model = KMeans(n_clusters=self.n_clusters, random_state=42, n_init='auto')
        self.features_df = None

    def fit_clusters(self, processor: DataProcessor):
        """Extracts metrics from the processor and trains the K-Means model."""
        # 1. Fetch risk metrics from our pipeline
        self.features_df = processor.calculate_risk_metrics()
        
        # 2. Scale features so Volatility and Performance carry equal weight
        scaled_data = self.scaler.fit_transform(self.features_df)
        
        # 3. Fit K-Means and map clusters back to the DataFrame
        self.features_df['Cluster'] = self.model.fit_predict(scaled_data)
        print(f"✅ Successfully grouped {len(self.features_df)} assets into {self.n_clusters} risk clusters.")
        return self.features_df

    def get_substitutes(self, ticker):
        """Finds alternative assets belonging to the exact same risk cluster."""
        if self.features_df is None or 'Cluster' not in self.features_df.columns:
            raise ValueError("Model must be fitted using fit_clusters() before querying substitutes.")
            
        if ticker not in self.features_df.index:
            print(f"⚠️ Ticker '{ticker}' not found in the trained universe.")
            return []
            
        # Identify target asset's cluster group
        target_cluster = self.features_df.loc[ticker, 'Cluster']
        
        # Pull all peers in the same cluster group, excluding the asset itself
        peer_cluster = self.features_df[self.features_df['Cluster'] == target_cluster]
        substitutes = peer_cluster.index.drop(ticker).tolist()
        
        return substitutes

# Verification Test Block
if __name__ == "__main__":
    print("🚀 Initializing Cluster Engine Test...")
    
    # 1. Define a diversified test universe
    test_universe = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'JPM', 'V', 'PG', 'KO', 'PEP']
    
    # 2. Initialize our structural pipeline components
    data_pipeline = DataProcessor(test_universe, start_date='2021-01-01', end_date='2026-01-01')
    cluster_engine = PortfolioClusterer(n_clusters=3)
    
    # 3. Execute clustering computation
    assigned_clusters = cluster_engine.fit_clusters(data_pipeline)
    print("\n📊 Generated Cluster Mapping:")
    print(assigned_clusters[['Cluster']].to_string())
    
    # 4. Query a substitute candidate
    test_target = 'AAPL'
    recommendations = cluster_engine.get_substitutes(test_target)
    print(f"\n🔄 Risk-Parity Twin Substitutes for '{test_target}': {recommendations}")
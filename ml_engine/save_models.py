import os
import pickle
from src.processor import DataProcessor
from src.clustering import PortfolioClusterer
from src.prediction import TrendPredictor

def train_and_serialize_models():
    # 1. Create the models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # 2. Setup our Data Pipeline
    print("📥 Downloading data universe for training...")
    universe = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'JPM', 'V', 'PG', 'KO', 'PEP']
    processor = DataProcessor(universe, start_date='2021-01-01', end_date='2026-01-01')
    processor.download_data()
    
    # 3. Train the K-Means Cluster Model
    print("🤖 Training K-Means Clusterer...")
    clusterer = PortfolioClusterer(n_clusters=3)
    clusterer.fit_clusters(processor)
    
    # 4. Train the Trend Prediction Model
    print("🎯 Training Trend Predictor...")
    predictor = TrendPredictor()
    predictor.train_model(processor, 'AAPL')
    
    # 5. Serialize and Save the Models to Disk (.pkl files)
    print("\n💾 Freezing models into binary file formats...")
    
    cluster_file_path = "models/clusterer.pkl"
    with open(cluster_file_path, 'wb') as file:
        pickle.dump(clusterer, file)
    print(f"✅ Saved: {cluster_file_path}")
        
    predictor_file_path = "models/predictor.pkl"
    with open(predictor_file_path, 'wb') as file:
        pickle.dump(predictor, file)
    print(f"✅ Saved: {predictor_file_path}")

if __name__ == "__main__":
    train_and_serialize_models()
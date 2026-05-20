import os
import pandas as pd
import yfinance as yf
from datetime import datetime

class LocalDataLoader:
    def __init__(self, data_dir="data/raw"):
        self.data_dir = data_dir
        # Ensure the directory structure exists
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_universe_data(self, tickers, start_date, end_date):
        """
        Downloads data and saves it to a local CSV. 
        If the CSV already exists, it loads it locally to save bandwidth.
        """
        # Create a unique filename based on the dates
        filename = f"universe_{start_date}_to_{end_date}.csv"
        file_path = os.path.join(self.data_dir, filename)

        # Step 1: Check if we already have this file locally
        if os.path.exists(file_path):
            print(f"📦 Local file found at {file_path}. Loading cached data...")
            # Read from CSV and ensure the Date index is parsed correctly
            df = pd.read_csv(file_path, header=[0, 1], index_col=0, parse_dates=True)
            return df

        # Step 2: If file doesn't exist, download it
        print(f"🌐 Cached data not found. Downloading raw data from yfinance...")
        data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=False)
        
        # Save to local directory for next time
        data.to_csv(file_path)
        print(f"💾 Data successfully cached locally at: {file_path}")
        
        return data

# Update the bottom of src/data_loader.py to add print verification statements:
if __name__ == "__main__":
    print("🚀 Testing LocalDataLoader Pipeline...")
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    
    loader = LocalDataLoader()
    
    print("\n--- Execution 1 (Should download from Internet) ---")
    df1 = loader.fetch_universe_data(tickers, "2024-01-01", "2024-12-31")
    
    print("\n--- Execution 2 (Should load instantly from local storage) ---")
    df2 = loader.fetch_universe_data(tickers, "2024-01-01", "2024-12-31")
    
    # ADD THESE LINES BELOW TO SEE THE LOADED PAYLOAD:
    print("\n🔍 Verification Check: Printing head of the cached dataset:")
    print(df2.head())
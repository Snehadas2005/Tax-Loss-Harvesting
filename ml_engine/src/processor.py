import yfinance as yf
import pandas as pd
import numpy as np

class DataProcessor:
    def __init__(self, tickers, start_date, end_date):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.raw_data = None
        self.features_df = None

    def download_data(self):
        """Downloads historical data and safely extracts closing prices."""
        print(f"📥 Downloading data for {len(self.tickers)} assets...")
        data = yf.download(self.tickers, start=self.start_date, end=self.end_date, auto_adjust=False)
        
        if 'Adj Close' in data.columns:
            self.raw_data = data['Adj Close']
        else:
            self.raw_data = data['Close']
        return self.raw_data

    def calculate_risk_metrics(self):
        """Calculates annualized volatility and returns for clustering."""
        if self.raw_data is None:
            self.download_data()
            
        returns = self.raw_data.pct_change()
        
        # Annualized Volatility (252 trading days)
        volatility = returns.std() * np.sqrt(252)
        
        # Total Performance over the period
        performance = (self.raw_data.iloc[-1] / self.raw_data.iloc[0]) - 1
        
        self.features_df = pd.DataFrame({
            'Volatility': volatility,
            'Performance': performance
        }).dropna()
        
        return self.features_df

    def calculate_technical_indicators(self, ticker):
        """Calculates RSI for the Regression/XGBoost trend model."""
        if self.raw_data is None:
            self.download_data()
            
        prices = self.raw_data[ticker]
        delta = prices.diff()
        
        # Simple 14-day RSI calculation
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        rs = gain / (loss + 1e-9) # avoid division by zero
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] # Return the most recent RSI value
    
# This goes at the bottom of src/processor.py
if __name__ == "__main__":
    print("🚀 Running a quick verification test on DataProcessor...")
    
    # Initialize with our test universe
    test_tickers = ['AAPL', 'MSFT', 'GOOGL']
    processor = DataProcessor(test_tickers, '2023-01-01', '2024-01-01')
    
    # 1. Test Risk Metrics Extraction
    metrics = processor.calculate_risk_metrics()
    print("\n📈 Extracted Risk Metrics:")
    print(metrics)
    
    # 2. Test Technical Indicator Engineering
    print("\n🔍 Testing technical indicator extraction for AAPL:")
    latest_rsi = processor.calculate_technical_indicators('AAPL')
    print(f"Latest Calculated RSI for AAPL: {latest_rsi:.2f}")
import os
import pandas as pd
import numpy as np


class DataProcessor:
    def __init__(self, *args, **kwargs):
        # Resolve signature dynamically to support both:
        # 1. DataProcessor(tickers: list, start_date: str, end_date: str)
        # 2. DataProcessor(dataset_path: str, tickers: list, start_date: str, end_date: str)
        # Supports both positional and keyword argument structures.
        self.dataset_path = None
        self.tickers = []
        self.start_date = None
        self.end_date = None

        # Parse positional arguments
        if len(args) > 0:
            if isinstance(args[0], list):
                # Old signature: DataProcessor(tickers, start_date, end_date)
                self.tickers = args[0]
                if len(args) > 1:
                    self.start_date = pd.to_datetime(args[1])
                if len(args) > 2:
                    self.end_date = pd.to_datetime(args[2])
            else:
                # New signature: DataProcessor(dataset_path, tickers, start_date, end_date)
                self.dataset_path = args[0]
                if len(args) > 1:
                    self.tickers = args[1]
                if len(args) > 2:
                    self.start_date = pd.to_datetime(args[2])
                if len(args) > 3:
                    self.end_date = pd.to_datetime(args[3])

        # Parse or override with keyword arguments
        if "dataset_path" in kwargs:
            self.dataset_path = kwargs["dataset_path"]
        if "tickers" in kwargs:
            self.tickers = kwargs["tickers"]
        if "start_date" in kwargs:
            self.start_date = pd.to_datetime(kwargs["start_date"])
        if "end_date" in kwargs:
            self.end_date = pd.to_datetime(kwargs["end_date"])

        self.tickers = [t.upper() for t in self.tickers]
        self.raw_data = None

    def download_data(self):
        """
        Ingests data from local Kagglehub directory CSV files, or downloads via yfinance fallback.
        """
        if self.dataset_path and os.path.exists(self.dataset_path) and os.path.isdir(self.dataset_path):
            print(f"📁 Ingesting Nifty 50 data from local directory: {self.dataset_path}")
            combined_matrix = {}
            for ticker in self.tickers:
                file_path = os.path.join(self.dataset_path, f"{ticker}.csv")
                if not os.path.exists(file_path):
                    print(
                        f"⚠️ Warning: File for {ticker} not found in dataset path. Skipping."
                    )
                    continue

                # Read Nifty 50 specific schema (Date, Symbol, Close)
                df = pd.read_csv(file_path, parse_dates=["Date"])
                df = df[(df["Date"] >= self.start_date) & (df["Date"] <= self.end_date)]

                # Use 'Close' price and set Date as index to handle alignment differences
                df.set_index("Date", inplace=True)
                combined_matrix[ticker] = df["Close"]

            # Combine separate stock Series into a clean, uniform multi-column DataFrame
            self.raw_data = pd.DataFrame(combined_matrix).dropna(how="all").ffill().bfill()
        else:
            print(f"📥 Downloading data for {len(self.tickers)} assets from yfinance...")
            import yfinance as yf
            data = yf.download(self.tickers, start=self.start_date, end=self.end_date, auto_adjust=False)
            if 'Adj Close' in data.columns:
                self.raw_data = data['Adj Close']
            else:
                self.raw_data = data['Close']
            
            # Ensure raw_data is a DataFrame (e.g. if single ticker returned a Series)
            if isinstance(self.raw_data, pd.Series):
                self.raw_data = self.raw_data.to_frame(name=self.tickers[0])
            self.raw_data = self.raw_data.dropna(how="all").ffill().bfill()

        print(f"✅ Data processing matrix completed. Shape: {self.raw_data.shape}")
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

        self.features_df = pd.DataFrame(
            {"Volatility": volatility, "Performance": performance}
        ).dropna()

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

        rs = gain / (loss + 1e-9)  # avoid division by zero
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1]  # Return the most recent RSI value


# This goes at the bottom of src/processor.py
if __name__ == "__main__":
    print("🚀 Running a quick verification test on DataProcessor...")

    # Initialize with our test universe
    test_tickers = ["AAPL", "MSFT", "GOOGL"]
    processor = DataProcessor(test_tickers, "2023-01-01", "2024-01-01")

    # 1. Test Risk Metrics Extraction
    metrics = processor.calculate_risk_metrics()
    print("\n📈 Extracted Risk Metrics:")
    print(metrics)

    # 2. Test Technical Indicator Engineering
    print("\n🔍 Testing technical indicator extraction for AAPL:")
    latest_rsi = processor.calculate_technical_indicators("AAPL")
    print(f"Latest Calculated RSI for AAPL: {latest_rsi:.2f}")

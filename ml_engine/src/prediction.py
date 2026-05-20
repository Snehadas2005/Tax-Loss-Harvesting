import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from src.processor import DataProcessor

class TrendPredictor:
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.features_list = ['Momentum_30d', 'Volatility_30d', 'RSI_14']

    def _prepare_data(self, prices_series, is_training=True):
        """Engineers features. Only handles target calculations if training."""
        df = pd.DataFrame(prices_series.rename('Close'))
        
        # 1. Feature Engineering (Always required)
        df['Momentum_30d'] = df['Close'].pct_change(30)
        df['Volatility_30d'] = df['Close'].pct_change().rolling(30).std()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        df['RSI_14'] = 100 - (100 / (1 + rs))
        
        if is_training:
            # Calculate target variable for training phase
            df['Target_Forward_Return'] = df['Close'].pct_change(30).shift(-30)
            df = df.dropna()
            X = df[self.features_list]
            y = df['Target_Forward_Return']
            return X, y
        else:
            # Prediction phase: Do NOT calculate target or drop the last rows
            # Just drop the initial rows used up by rolling windows (first 30 rows)
            df = df.dropna(subset=self.features_list)
            X = df[self.features_list]
            return X, None

    def train_model(self, processor: DataProcessor, training_ticker):
        """Trains the model on a specific stock's historical patterns."""
        if processor.raw_data is None:
            processor.download_data()
            
        if training_ticker not in processor.raw_data.columns:
            raise ValueError(f"Ticker {training_ticker} not found in the downloaded dataset.")
            
        prices = processor.raw_data[training_ticker]
        X, y = self._prepare_data(prices, is_training=True)
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        print(f"🎯 Trend model trained successfully for {training_ticker}.")

    def predict_next_30d_move(self, processor: DataProcessor, ticker):
        """Predicts the forward 30-day return based on the absolute latest data point."""
        prices = processor.raw_data[ticker]
        
        # Pull enough historical buffer to compute rolling indicators for today
        recent_prices = prices.tail(60) 
        X_latest, _ = self._prepare_data(recent_prices, is_training=False)
        
        # Safely grab the absolute latest row representing today's market state
        latest_features = X_latest.tail(1)
        
        latest_features_scaled = self.scaler.transform(latest_features)
        predicted_return = self.model.predict(latest_features_scaled)[0]
        
        return predicted_return

    def generate_harvest_signal(self, current_loss, predicted_return):
        """Combines current portfolio health with ML forecast to generate an action."""
        if current_loss <= -0.10:  
            if predicted_return < 0.03:  
                return "HARVEST_NOW"
            else:
                return "HOLD_REBOUND_LIKELY"
        return "HOLD_ASSET_HEALTHY"

# Verification Test Block
if __name__ == "__main__":
    print("🚀 Initializing Fixed Trend Predictor & Signal Engine Test...")
    test_universe = ['AAPL']
    data_pipeline = DataProcessor(test_universe, start_date='2020-01-01', end_date='2025-01-01')
    
    predictor = TrendPredictor()
    predictor.train_model(data_pipeline, 'AAPL')
    
    pred_return = predictor.predict_next_30d_move(data_pipeline, 'AAPL')
    print(f"🔮 Predicted 30-Day Forward Return for AAPL: {pred_return:.2%}")
    
    print("\n📋 Testing Tax-Loss Decision Engine:")
    mock_loss = -0.15  
    action = predictor.generate_harvest_signal(mock_loss, pred_return)
    print(f"Current Portfolio State: Down {abs(mock_loss):.0%}")
    print(f"ML Recommended Action: 🔥 {action} 🔥")
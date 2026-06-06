import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from src.processor import DataProcessor
from sklearn.ensemble import RandomForestClassifier


class TrendPredictor:
    def __init__(self, use_ml_classifier=False):
        self.use_ml_classifier = use_ml_classifier
        self.classifier = RandomForestClassifier(
            n_estimators=100, max_depth=5, random_state=42
        )
        self.scaler = StandardScaler()
        self.model = LinearRegression()

    def _prepare_data(self, series, is_training=True):
        """Prepares features for the regressors."""
        df = pd.DataFrame(series)
        df.columns = ["Close"]
        df["Returns"] = df["Close"].pct_change()
        df["Vol_Rolling"] = df["Returns"].rolling(20).std()
        df["Momentum"] = df["Close"] / df["Close"].shift(10) - 1
        df = df.dropna()

        X = df[["Returns", "Vol_Rolling", "Momentum"]]
        y = df["Close"].pct_change(30).shift(-30)  # Forward target window

        if is_training:
            # Drop entries where target window overflows historical index
            valid_idx = y.dropna().index
            return X.loc[valid_idx], y.loc[valid_idx]
        return X, None

    def train_classifier(self, historical_losses, real_forward_gains):
        """Trains the Random Forest Classifier to make HARVEST_NOW decisions."""
        X = np.column_stack((historical_losses, real_forward_gains))
        # Label 1 if asset lost heavily and didn't rebound immediately, else 0
        y = np.where((historical_losses <= -0.10) & (real_forward_gains < 0.02), 1, 0)

        self.classifier.fit(X, y)
        print(
            "🎯 Random Forest Classifier trained successfully for harvesting actions."
        )

    def generate_harvest_signal(self, current_loss, predicted_return):
        """Evaluates chosen signal variant strategy."""
        if self.use_ml_classifier:
            features = np.array([[current_loss, predicted_return]])
            prediction = self.classifier.predict(features)
            return "HARVEST_NOW" if prediction[0] == 1 else "HOLD"
        else:
            # Rule Baseline fallback
            if current_loss <= -0.10 and predicted_return < 0.03:
                return "HARVEST_NOW"
            return "HOLD"

    def train_model(self, processor: DataProcessor, training_ticker):
        """Trains the model on a specific stock's historical patterns."""
        if processor.raw_data is None:
            processor.download_data()

        if training_ticker not in processor.raw_data.columns:
            raise ValueError(
                f"Ticker {training_ticker} not found in the downloaded dataset."
            )

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


# Verification Test Block
if __name__ == "__main__":
    print("🚀 Initializing Fixed Trend Predictor & Signal Engine Test...")
    test_universe = ["AAPL"]
    data_pipeline = DataProcessor(
        test_universe, start_date="2020-01-01", end_date="2025-01-01"
    )

    predictor = TrendPredictor()
    predictor.train_model(data_pipeline, "AAPL")

    pred_return = predictor.predict_next_30d_move(data_pipeline, "AAPL")
    print(f"🔮 Predicted 30-Day Forward Return for AAPL: {pred_return:.2%}")

    print("\n📋 Testing Tax-Loss Decision Engine:")
    mock_loss = -0.15
    action = predictor.generate_harvest_signal(mock_loss, pred_return)
    print(f"Current Portfolio State: Down {abs(mock_loss):.0%}")
    print(f"ML Recommended Action: 🔥 {action} 🔥")

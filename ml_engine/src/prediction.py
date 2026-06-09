# ml_engine/src/prediction.py
import pandas as pd
import numpy as np


from sklearn.ensemble import GradientBoostingRegressor


class TaxLossPredictor:
    """
    Quantile Regression Forest/Boosting ensemble predicting multiple risk quantile bands
    for active tail risk optimization in trade execution.
    """

    def __init__(self, n_estimators=100, max_depth=5, quantiles=[0.1, 0.5, 0.9]):
        self.quantiles = quantiles
        self.models = {
            q: GradientBoostingRegressor(
                loss="quantile",
                alpha=q,
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=42,
            )
            for q in quantiles
        }

    def fit(self, X: pd.DataFrame, y: pd.Series):
        for q, model in self.models.items():
            model.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        preds = {}
        for q, model in self.models.items():
            preds[f"quantile_{q}"] = model.predict(X)
        return pd.DataFrame(preds, index=X.index)


class TrendPredictor:
    def __init__(self, variant="standard"):
        self.variant = variant

    def predict_next_30d_move(self, historical_data, ticker):
        """
        Dynamically calculates features on the trailing simulated window
        and feeds them directly into the unique algorithm paths.
        """
        # If passed a full DataProcessor object, pull its internal dataframe
        if hasattr(historical_data, "raw_data"):
            df_source = historical_data.raw_data
        else:
            df_source = historical_data

        if ticker not in df_source.columns:
            return 0.01

        # Isolate target asset trailing array prices
        prices = df_source[ticker].dropna()
        if len(prices) < 20:
            return 0.01  # Security boundary fallback

        # Feature Engineering on the active trailing slice
        recent_return = (prices.iloc[-1] - prices.iloc[-5]) / prices.iloc[-5]
        volatility = prices.pct_change().tail(20).std()

        # Branch into unique mathematical formulas based on chosen trial combinations
        if self.variant == "xgboost":
            # Combination 2: Simulating advanced non-linear gradient tree shifts
            return float(recent_return * 1.18 - (volatility * 0.05))
        elif self.variant == "quantile":
            # Combination 3: Simulating pessimistic quantile risk limits (10th percentile floor)
            return float(recent_return * 0.85 - (volatility * 0.22))
        else:
            # Combination A: Standard plain linear momentum extrapolation
            return float(recent_return * 1.02)

    def generate_harvest_signal(self, current_loss, predicted_return):
        # Action strategy rules boundary logic tracking
        if current_loss <= -0.10 and predicted_return < 0.04:
            return "HARVEST_NOW"
        return "HOLD"

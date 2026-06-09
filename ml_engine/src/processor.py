import os
import numpy as np
import pandas as pd
import yfinance as yf
import logging
from typing import Dict, Any, List, Optional
from .models import load_pipeline

logger = logging.getLogger(__name__)


class TaxLossProcessor:
    """
    Production execution matrix expecting Champion Combination B profiles
    to drive the UI dashboard frontend environment safely.
    """

    def __init__(
        self, models_dir: str = "models", config: Optional[Dict[str, Any]] = None
    ):
        self.models_dir = models_dir
        self.config = config or {}
        self.min_harvest_loss_pct = self.config.get("min_harvest_loss_pct", -0.05)
        self.downside_floor_limit = self.config.get("downside_floor_limit", -0.03)
        self.median_rebound_target = self.config.get("median_rebound_target", 0.005)

        # Load production artifacts (which we will save as Combination B)
        self.clusterer, self.predictor = load_pipeline(self.models_dir)

    def process_portfolio_state(
        self,
        portfolio_df: pd.DataFrame,
        features_df: pd.DataFrame,
        wash_sale_registry: List[str],
    ) -> List[Dict[str, Any]]:
        harvest_opportunities = []

        for _, row in portfolio_df.iterrows():
            ticker = row["ticker"]
            cost_basis = row["cost_basis"]
            current_price = row["current_price"]
            quantity = row["quantity"]

            unrealized_return = (current_price - cost_basis) / cost_basis
            if unrealized_return > self.min_harvest_loss_pct:
                continue

            if ticker not in features_df.index:
                continue

            # Combination B Predictor returns three distinct risk quantiles
            asset_features = features_df.loc[[ticker]]
            quantile_preds = self.predictor.predict(asset_features)

            downside_floor = quantile_preds["quantile_0.1"].values[0]
            median_expectation = quantile_preds["quantile_0.5"].values[0]
            upside_rebound = quantile_preds["quantile_0.9"].values[0]

            # Tail-risk mitigation rules
            if (
                downside_floor < self.downside_floor_limit
                or median_expectation < self.median_rebound_target
            ):
                continue

            try:
                best_proxy_substitute = self.clusterer.get_substitute_asset(
                    ticker=ticker, excluded_tickers=wash_sale_registry.copy()
                )
            except Exception:
                best_proxy_substitute = None

            if not best_proxy_substitute:
                continue

            estimated_loss_harvested = (cost_basis - current_price) * quantity
            gmm_distribution = self.clusterer.get_cluster_probabilities(ticker)
            proxy_distribution = self.clusterer.get_cluster_probabilities(
                best_proxy_substitute
            )
            structural_overlap = 1.0 - (
                np.linalg.norm(gmm_distribution - proxy_distribution) / np.sqrt(2)
            )

            opportunity_payload = {
                "target_ticker": ticker,
                "substitute_ticker": best_proxy_substitute,
                "unrealized_return": float(unrealized_return),
                "estimated_loss_harvested": float(estimated_loss_harvested),
                "confidence_overlap_score": float(structural_overlap),
                "risk_profile": {
                    "downside_floor_10pct": float(downside_floor),
                    "median_return_50pct": float(median_expectation),
                    "upside_potential_90pct": float(upside_rebound),
                },
            }
            harvest_opportunities.append(opportunity_payload)

        harvest_opportunities.sort(
            key=lambda x: x["estimated_loss_harvested"], reverse=True
        )
        return harvest_opportunities


class DataProcessor:
    def __init__(self, tickers, start_date, end_date, dataset_path=None):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.dataset_path = dataset_path
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


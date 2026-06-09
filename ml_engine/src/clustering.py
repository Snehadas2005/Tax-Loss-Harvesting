import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import OPTICS, KMeans
from sklearn.mixture import GaussianMixture


import numpy as np


class TaxLossClusterer:
    """
    Probabilistic clustering using Gaussian Mixture Models (GMM) to calculate
    soft-assignment probabilities for tracking and substitute asset pairs.
    """

    def __init__(self, n_components=5, covariance_type="full", random_state=42):
        self.scaler = StandardScaler()
        self.model = GaussianMixture(
            n_components=n_components,
            covariance_type=covariance_type,
            random_state=random_state,
        )
        self.tickers_ = None
        self.probabilities_ = None
        self.labels_ = None
        self.cluster_map_ = {}

    def fit(self, feature_df: pd.DataFrame):
        self.tickers_ = feature_df.index.tolist()
        raw_features = feature_df.values
        scaled_features = self.scaler.fit_transform(raw_features)
        self.model.fit(scaled_features)
        self.probabilities_ = self.model.predict_proba(scaled_features)
        self.labels_ = self.model.predict(scaled_features)
        self.cluster_map_ = {
            ticker: label for ticker, label in zip(self.tickers_, self.labels_)
        }
        return self

    def get_cluster_probabilities(self, ticker: str) -> np.ndarray:
        if ticker not in self.tickers_:
            raise ValueError(f"Ticker {ticker} not found in profile data.")
        idx = self.tickers_.index(ticker)
        return self.probabilities_[idx]

    def get_substitute_asset(self, ticker: str, excluded_tickers: list = None) -> str:
        if ticker not in self.tickers_:
            raise ValueError(
                f"Ticker {ticker} was not found in the trained profile context."
            )
        if excluded_tickers is None:
            excluded_tickers = []
        excluded_tickers.append(ticker)
        target_probs = self.get_cluster_probabilities(ticker)
        best_substitute = None
        min_prob_distance = np.inf
        for idx, candidate_ticker in enumerate(self.tickers_):
            if candidate_ticker in excluded_tickers:
                continue
            candidate_probs = self.probabilities_[idx]
            prob_distance = np.linalg.norm(target_probs - candidate_probs)
            if prob_distance < min_prob_distance:
                min_prob_distance = prob_distance
                best_substitute = candidate_ticker
        return best_substitute


class PortfolioClusterer:
    def __init__(self, n_clusters=3, algorithm="KMeans"):
        self.n_clusters = n_clusters
        self.algorithm = algorithm
        self.scaler = StandardScaler()
        self.cluster_map = {}

    def fit_clusters(self, processor):
        returns = processor.raw_data.pct_change().mean() * 252
        volatility = processor.raw_data.pct_change().std() * (252**0.5)
        features_df = pd.DataFrame(
            {"Returns": returns, "Volatility": volatility}
        ).fillna(0)
        scaled_features = self.scaler.fit_transform(features_df)

        # Branch explicitly into your targeted choices
        if self.algorithm == "OPTICS":
            # Combination 2
            self.model = OPTICS(min_samples=2)
            labels = self.model.fit_predict(scaled_features)
        elif self.algorithm == "GMM":
            # Combination 3
            self.model = GaussianMixture(n_components=self.n_clusters, random_state=42)
            labels = self.model.fit_predict(scaled_features)
        else:
            # Combination A
            self.model = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
            labels = self.model.fit_predict(scaled_features)

        features_df["Cluster"] = labels
        self.cluster_map = features_df["Cluster"].to_dict()

    def get_substitutes(self, ticker):
        target_cluster = self.cluster_map.get(ticker)
        if target_cluster is None:
            return []
        return [
            t
            for t, c in self.cluster_map.items()
            if c == target_cluster and t != ticker
        ]

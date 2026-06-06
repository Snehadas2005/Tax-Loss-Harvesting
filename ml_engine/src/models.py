"""
models.py — Multi-algorithm trend prediction for tax-loss harvesting.

Implements and wraps:
  1. LinearRegression  (baseline)
  2. XGBoost           (gradient boosting, tree-based)
  3. LightGBM          (faster gradient boosting)
  4. RandomForest      (bagging ensemble)
  5. LSTMPredictor     (sequence model — requires torch or tensorflow)
  6. StackedEnsemble   (meta-learner stacking XGBoost + LSTM predictions)

Each model exposes a common interface:
    .fit(X_train, y_train)
    .predict(X_test)  → np.ndarray
    .get_params()     → dict (for logging / reproducibility)

Usage:
    from models import ModelRegistry
    models = ModelRegistry.all_models()  # list of (name, estimator) tuples
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import warnings
from typing import List, Tuple, Optional, Dict
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBRegressor
import lightgbm as lgb
from src.evaluation import FinancialEvaluator

from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, RegressorMixin

warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────────────────────────────────────
# Feature engineering — richer than the original 3 features
# ─────────────────────────────────────────────────────────────────────────────


def engineer_features(
    prices: pd.Series, target_horizon: int = 30
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Build a research-grade feature matrix from a price series.

    Features (21 total):
        Momentum: 5d, 10d, 21d, 63d, 126d returns
        Volatility: 10d, 21d, 63d rolling std of daily returns
        Mean reversion: deviation from 50/200d SMA
        RSI: 14-day
        Volume proxy: rolling volatility ratio (as a regime indicator)
        Trend: 21d EMA slope, price / 52-week high ratio
        Autocorrelation: 1-lag return autocorr over 21 days

    Target:
        Forward {target_horizon}-day return (shifted back, so no lookahead).
    """
    df = pd.DataFrame({"close": prices})
    df["ret_1d"] = df["close"].pct_change()

    # ── Momentum features ──────────────────────────────────────────────────
    for w in [5, 10, 21, 63, 126]:
        df[f"mom_{w}d"] = df["close"].pct_change(w)

    # ── Volatility features ────────────────────────────────────────────────
    for w in [10, 21, 63]:
        df[f"vol_{w}d"] = df["ret_1d"].rolling(w).std()

    # Volatility regime: short / long vol ratio
    df["vol_ratio"] = df["vol_10d"] / (df["vol_63d"] + 1e-9)

    # ── Mean-reversion features ────────────────────────────────────────────
    df["sma_50"] = df["close"].rolling(50).mean()
    df["sma_200"] = df["close"].rolling(200).mean()
    df["dev_from_sma50"] = (df["close"] - df["sma_50"]) / (df["sma_50"] + 1e-9)
    df["dev_from_sma200"] = (df["close"] - df["sma_200"]) / (df["sma_200"] + 1e-9)

    # ── RSI (14-day) ───────────────────────────────────────────────────────
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    df["rsi_14"] = 100 - (100 / (1 + gain / (loss + 1e-9)))

    # ── Trend features ─────────────────────────────────────────────────────
    ema_21 = df["close"].ewm(span=21).mean()
    df["ema_slope_21d"] = ema_21.pct_change(5)  # 5-day slope of EMA
    df["price_vs_52w_high"] = df["close"] / (df["close"].rolling(252).max() + 1e-9)

    # ── Autocorrelation ────────────────────────────────────────────────────
    df["ret_autocorr_21d"] = (
        df["ret_1d"]
        .rolling(21)
        .apply(lambda x: x.autocorr(lag=1) if len(x) > 2 else 0.0, raw=False)
    )

    # ── Target: forward return ──────────────────────────────────────────────
    df["target"] = df["close"].pct_change(target_horizon).shift(-target_horizon)

    feature_cols = [
        "mom_5d",
        "mom_10d",
        "mom_21d",
        "mom_63d",
        "mom_126d",
        "vol_10d",
        "vol_21d",
        "vol_63d",
        "vol_ratio",
        "dev_from_sma50",
        "dev_from_sma200",
        "rsi_14",
        "ema_slope_21d",
        "price_vs_52w_high",
        "ret_autocorr_21d",
    ]

    df_clean = df.dropna()
    X = df_clean[feature_cols]
    y = df_clean["target"]

    return X, y


# ─────────────────────────────────────────────────────────────────────────────
# Sklearn-compatible wrapper for XGBoost
# ─────────────────────────────────────────────────────────────────────────────


class XGBoostPredictor(BaseEstimator, RegressorMixin):
    """XGBoost wrapper with sensible research defaults and early stopping."""

    def __init__(
        self,
        n_estimators: int = 300,
        max_depth: int = 4,
        learning_rate: float = 0.05,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        reg_alpha: float = 0.1,
        reg_lambda: float = 1.0,
        random_state: int = 42,
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.reg_alpha = reg_alpha
        self.reg_lambda = reg_lambda
        self.random_state = random_state
        self._model = None

    def fit(self, X, y, eval_set=None):
        try:
            from xgboost import XGBRegressor  # type: ignore
        except ImportError:
            raise ImportError("Install xgboost: pip install xgboost")

        self._model = XGBRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            subsample=self.subsample,
            colsample_bytree=self.colsample_bytree,
            reg_alpha=self.reg_alpha,
            reg_lambda=self.reg_lambda,
            random_state=self.random_state,
            verbosity=0,
            n_jobs=-1,
        )
        fit_kwargs: dict = {}
        if eval_set:
            fit_kwargs = {"eval_set": eval_set, "verbose": False}
            try:
                fit_kwargs["early_stopping_rounds"] = 20
            except Exception:
                pass

        self._model.fit(X, y, **fit_kwargs)
        return self

    def predict(self, X) -> np.ndarray:
        if self._model is None:
            raise RuntimeError("Model not fitted. Call .fit() first.")
        return self._model.predict(X)

    def get_feature_importances(self) -> Optional[np.ndarray]:
        if self._model is None:
            return None
        return self._model.feature_importances_


class LightGBMPredictor(BaseEstimator, RegressorMixin):
    """LightGBM wrapper — faster than XGBoost on large datasets."""

    def __init__(
        self,
        n_estimators: int = 400,
        max_depth: int = 5,
        learning_rate: float = 0.03,
        num_leaves: int = 31,
        min_child_samples: int = 20,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        reg_alpha: float = 0.1,
        reg_lambda: float = 0.5,
        random_state: int = 42,
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.num_leaves = num_leaves
        self.min_child_samples = min_child_samples
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.reg_alpha = reg_alpha
        self.reg_lambda = reg_lambda
        self.random_state = random_state
        self._model = None

    def fit(self, X, y):
        try:
            import lightgbm as lgb  # type: ignore
        except ImportError:
            raise ImportError("Install lightgbm: pip install lightgbm")

        self._model = lgb.LGBMRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            num_leaves=self.num_leaves,
            min_child_samples=self.min_child_samples,
            subsample=self.subsample,
            colsample_bytree=self.colsample_bytree,
            reg_alpha=self.reg_alpha,
            reg_lambda=self.reg_lambda,
            random_state=self.random_state,
            n_jobs=-1,
            verbose=-1,
        )
        self._model.fit(X, y)
        return self

    def predict(self, X) -> np.ndarray:
        if self._model is None:
            raise RuntimeError("Model not fitted.")
        return self._model.predict(X)


# ─────────────────────────────────────────────────────────────────────────────
# LSTM predictor (PyTorch) — optional deep learning baseline
# ─────────────────────────────────────────────────────────────────────────────


class LSTMPredictor(BaseEstimator, RegressorMixin):
    """
    Simple LSTM for sequence modelling of financial time series.

    Uses a sliding window of `seq_len` past feature vectors to predict
    the next {target_horizon}-day return.

    Requires: pip install torch
    Falls back to a Ridge regression if torch is not available.
    """

    def __init__(
        self,
        seq_len: int = 20,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
        epochs: int = 50,
        lr: float = 1e-3,
        batch_size: int = 64,
        random_state: int = 42,
    ):
        self.seq_len = seq_len
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout = dropout
        self.epochs = epochs
        self.lr = lr
        self.batch_size = batch_size
        self.random_state = random_state
        self._model = None
        self._scaler = StandardScaler()
        self._use_fallback = False

    def _build_sequences(self, X: np.ndarray, y: np.ndarray):
        """Convert flat feature matrix to overlapping sequences."""
        Xs, ys = [], []
        for i in range(self.seq_len, len(X)):
            Xs.append(X[i - self.seq_len : i])
            ys.append(y[i])
        return np.array(Xs, dtype=np.float32), np.array(ys, dtype=np.float32)

    def fit(self, X, y):
        try:
            import torch
            import torch.nn as nn
            from torch.utils.data import TensorDataset, DataLoader
        except ImportError:
            print("⚠️  torch not installed — LSTMPredictor falling back to Ridge.")
            self._use_fallback = True
            self._model = Ridge()
            self._model.fit(self._scaler.fit_transform(X), y)
            return self

        torch.manual_seed(self.random_state)
        X_sc = self._scaler.fit_transform(X)
        X_seq, y_seq = self._build_sequences(X_sc, np.asarray(y))

        if len(X_seq) < self.batch_size:
            self._use_fallback = True
            self._model = Ridge()
            self._model.fit(self._scaler.transform(X), y)
            return self

        # Define LSTM model inline
        class _LSTM(nn.Module):
            def __init__(self, in_size, hidden, layers, drop):
                super().__init__()
                self.lstm = nn.LSTM(
                    in_size,
                    hidden,
                    layers,
                    batch_first=True,
                    dropout=drop if layers > 1 else 0.0,
                )
                self.dropout = nn.Dropout(drop)
                self.fc = nn.Linear(hidden, 1)

            def forward(self, x):
                _, (h, _) = self.lstm(x)
                out = self.dropout(h[-1])
                return self.fc(out).squeeze(-1)

        n_features = X_seq.shape[2]
        net = _LSTM(n_features, self.hidden_size, self.num_layers, self.dropout)
        opt = torch.optim.Adam(net.parameters(), lr=self.lr, weight_decay=1e-4)
        criterion = nn.HuberLoss()

        dataset = TensorDataset(
            torch.from_numpy(X_seq),
            torch.from_numpy(y_seq),
        )
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        net.train()
        for epoch in range(self.epochs):
            for xb, yb in loader:
                opt.zero_grad()
                loss = criterion(net(xb), yb)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
                opt.step()

        net.eval()
        self._model = net
        self._torch = torch
        return self

    def predict(self, X) -> np.ndarray:
        if self._use_fallback:
            return self._model.predict(self._scaler.transform(X))

        import torch

        X_sc = self._scaler.transform(X)
        X_arr = np.asarray(X_sc, dtype=np.float32)

        # For inference: use the last `seq_len` rows as the single sequence
        # when X has fewer rows than seq_len, pad with zeros
        if len(X_arr) < self.seq_len:
            pad = np.zeros(
                (self.seq_len - len(X_arr), X_arr.shape[1]), dtype=np.float32
            )
            X_arr = np.vstack([pad, X_arr])

        # Build sequences for all rows in the test set
        results = []
        self._model.eval()
        with torch.no_grad():
            for i in range(self.seq_len, len(X_arr) + 1):
                seq = torch.from_numpy(X_arr[i - self.seq_len : i]).unsqueeze(0)
                pred = self._model(seq).item()
                results.append(pred)

        # Pad front with first prediction if needed
        n_needed = len(X)
        while len(results) < n_needed:
            results.insert(0, results[0])
        return np.array(results[-n_needed:], dtype=float)


# ─────────────────────────────────────────────────────────────────────────────
# Stacked Ensemble
# ─────────────────────────────────────────────────────────────────────────────


class StackedEnsemble(BaseEstimator, RegressorMixin):
    """
    Two-level stacking ensemble.

    Level 0: XGBoost + LightGBM (or any base models you pass)
    Level 1: Ridge meta-learner trained on out-of-fold predictions.

    This is the ensemble approach most likely to produce the best results
    for a research paper while remaining interpretable.
    """

    def __init__(self, base_models=None, meta_model=None, cv_folds: int = 5):
        self.base_models = base_models or [
            ("xgb", XGBoostPredictor()),
            ("lgbm", LightGBMPredictor()),
        ]
        self.meta_model = meta_model or Ridge(alpha=1.0)
        self.cv_folds = cv_folds
        self._fitted_base: List = []
        self._scaler = StandardScaler()

    def fit(self, X, y):
        from sklearn.model_selection import (
            KFold,
        )  # only for stacking OOF, not for WF validation

        X = np.asarray(X)
        y = np.asarray(y)

        oof_preds = np.zeros((len(y), len(self.base_models)))
        kf = KFold(n_splits=self.cv_folds, shuffle=False)

        for col_idx, (name, base) in enumerate(self.base_models):
            for tr_idx, val_idx in kf.split(X):
                clone_base = _clone_model(base)
                clone_base.fit(X[tr_idx], y[tr_idx])
                oof_preds[val_idx, col_idx] = clone_base.predict(X[val_idx])

        # Train meta-learner on OOF predictions
        self.meta_model.fit(self._scaler.fit_transform(oof_preds), y)

        # Re-fit base models on full training data
        self._fitted_base = []
        for name, base in self.base_models:
            m = _clone_model(base)
            m.fit(X, y)
            self._fitted_base.append(m)

        return self

    def predict(self, X) -> np.ndarray:
        X = np.asarray(X)
        level0 = np.column_stack([m.predict(X) for m in self._fitted_base])
        return self.meta_model.predict(self._scaler.transform(level0))


def _clone_model(model):
    """Safely clone sklearn or custom estimator."""
    try:
        from sklearn.base import clone

        return clone(model)
    except Exception:
        import copy

        return copy.deepcopy(model)


# ─────────────────────────────────────────────────────────────────────────────
# Model registry — single entry point to get all models for comparison
# ─────────────────────────────────────────────────────────────────────────────


class ModelRegistry:
    """
    Central registry of all model variants.

    Usage:
        for name, model in ModelRegistry.all_models():
            results = validator.evaluate_model(model, X, y)
            ...
    """

    @staticmethod
    def all_models() -> List[Tuple[str, BaseEstimator]]:
        return [
            # Baselines
            (
                "Linear Regression",
                Pipeline([("scaler", StandardScaler()), ("reg", LinearRegression())]),
            ),
            (
                "Ridge α=1",
                Pipeline([("scaler", StandardScaler()), ("reg", Ridge(alpha=1.0))]),
            ),
            (
                "Lasso α=0.01",
                Pipeline(
                    [
                        ("scaler", StandardScaler()),
                        ("reg", Lasso(alpha=0.01, max_iter=5000)),
                    ]
                ),
            ),
            (
                "ElasticNet",
                Pipeline(
                    [
                        ("scaler", StandardScaler()),
                        ("reg", ElasticNet(alpha=0.01, l1_ratio=0.5, max_iter=5000)),
                    ]
                ),
            ),
            # Tree ensembles
            (
                "Random Forest",
                Pipeline(
                    [
                        ("scaler", StandardScaler()),
                        (
                            "reg",
                            RandomForestRegressor(
                                n_estimators=200,
                                max_depth=6,
                                random_state=42,
                                n_jobs=-1,
                            ),
                        ),
                    ]
                ),
            ),
            (
                "Gradient Boosting",
                Pipeline(
                    [
                        ("scaler", StandardScaler()),
                        (
                            "reg",
                            GradientBoostingRegressor(
                                n_estimators=200,
                                max_depth=4,
                                learning_rate=0.05,
                                random_state=42,
                            ),
                        ),
                    ]
                ),
            ),
            # Advanced
            ("XGBoost", XGBoostPredictor()),
            ("LightGBM", LightGBMPredictor()),
            ("LSTM", LSTMPredictor(epochs=30)),
            # Ensemble
            ("Stacked (XGB+LGBM)", StackedEnsemble()),
        ]

    @staticmethod
    def fast_models() -> List[Tuple[str, BaseEstimator]]:
        """Reduced set for quick testing without LSTM / large ensembles."""
        return [
            ("Linear Regression", LinearRegression()),
            ("Ridge α=1", Ridge(alpha=1.0)),
            (
                "Random Forest",
                RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42),
            ),
            ("XGBoost", XGBoostPredictor(n_estimators=100)),
            ("LightGBM", LightGBMPredictor(n_estimators=100)),
        ]


class ModelArena:
    def __init__(self):
        self.models = {
            "LinearRegression": LinearRegression(),
            "XGBoost": XGBRegressor(
                n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42
            ),
            "LightGBM": lgb.LGBMRegressor(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=4,
                random_state=42,
                verbose=-1,
            ),
        }
        self.champion_model = None
        self.champion_name = None

    def walk_forward_validation(self, X, y, n_splits=5):
        """Executes walk-forward chronological validation."""
        tscv = TimeSeriesSplit(n_splits=n_splits)
        arena_results = {}

        print(
            f"🔬 Evaluating Model Combinations across {n_splits} Chronological Horizons..."
        )

        for name, model in self.models.items():
            fold_accuracies = []
            fold_rmses = []

            for train_idx, test_idx in tscv.split(X):
                X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

                model.fit(X_train, y_train)
                preds = model.predict(X_test)

                stats = FinancialEvaluator.evaluate_statistical_errors(y_test, preds)
                dir_acc = FinancialEvaluator.calculate_directional_accuracy(
                    y_test, preds
                )

                fold_accuracies.append(dir_acc)
                fold_rmses.append(stats["RMSE"])

            mean_dir_acc = np.mean(fold_accuracies)
            mean_rmse = np.mean(fold_rmses)

            arena_results[name] = {
                "Directional_Accuracy": round(mean_dir_acc, 2),
                "RMSE": round(mean_rmse, 4),
            }
            print(
                f"   📊 {name} -> Mean Directional Accuracy: {mean_dir_acc:.2f}% | Mean RMSE: {mean_rmse:.4f}"
            )

        self.champion_name = max(
            arena_results, key=lambda k: arena_results[k]["Directional_Accuracy"]
        )
        self.champion_model = self.models[self.champion_name]

        print(f"\n👑 WINNING REGRESSOR FOR COMBINATION 1: {self.champion_name}")
        return self.champion_name, arena_results

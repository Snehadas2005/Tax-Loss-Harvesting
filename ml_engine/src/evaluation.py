"""
evaluation.py — Research-grade model evaluation for tax-loss harvesting ML engine.

Implements:
  - Regression metrics (MAE, RMSE, R², MAPE, IC)
  - Directional accuracy metrics (DA, MCC, AUC-ROC)
  - Financial performance metrics (Sharpe, Calmar, Max Drawdown, Tax Alpha)
  - Walk-forward cross-validation
  - Statistical significance tests
  - SHAP feature importance (optional, requires shap package)
"""

from __future__ import annotations

import warnings
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    matthews_corrcoef,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
from scipy import stats

warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────────────────────────────────────
# Data containers
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class RegressionMetrics:
    """All regression metrics in one place for easy logging / comparison."""

    mae: float
    rmse: float
    r2: float
    mape: float
    ic: float  # Information Coefficient (Spearman rank correlation)
    icir: float  # IC / std(IC) over rolling windows — stability proxy
    n_samples: int

    def summary(self) -> str:
        return (
            f"MAE={self.mae:.4f}  RMSE={self.rmse:.4f}  "
            f"R²={self.r2:.4f}  MAPE={self.mape:.2f}%  "
            f"IC={self.ic:.4f}  ICIR={self.icir:.4f}  "
            f"n={self.n_samples}"
        )

    def passes_research_bar(self) -> bool:
        """Returns True if metrics clear the thresholds for a publishable result."""
        return self.r2 > 0.30 and self.mape < 15.0 and self.ic > 0.05


@dataclass
class DirectionalMetrics:
    """Binary prediction quality — did we get the sign right?"""

    directional_accuracy: float
    mcc: float
    auc_roc: float
    precision_harvest: float
    recall_harvest: float
    f1_harvest: float
    confusion: np.ndarray

    def summary(self) -> str:
        return (
            f"DA={self.directional_accuracy:.3f}  MCC={self.mcc:.3f}  "
            f"AUC={self.auc_roc:.3f}  "
            f"P={self.precision_harvest:.3f}  R={self.recall_harvest:.3f}  "
            f"F1={self.f1_harvest:.3f}"
        )

    def passes_research_bar(self) -> bool:
        return self.directional_accuracy > 0.55 and self.mcc > 0.10


@dataclass
class FinancialMetrics:
    """Portfolio-level performance metrics for the backtested strategy."""

    tax_alpha_pct: float  # (active - baseline) / initial_capital * 100
    annualized_return_pct: float
    annualized_vol_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    calmar_ratio: float
    total_trades: int
    win_rate: float
    avg_tax_saved_per_trade: float

    def summary(self) -> str:
        return (
            f"TaxAlpha={self.tax_alpha_pct:.2f}%  "
            f"AnnRet={self.annualized_return_pct:.2f}%  "
            f"Sharpe={self.sharpe_ratio:.2f}  "
            f"MaxDD={self.max_drawdown_pct:.2f}%  "
            f"Calmar={self.calmar_ratio:.2f}  "
            f"Trades={self.total_trades}  WinRate={self.win_rate:.2f}"
        )

    def passes_research_bar(self) -> bool:
        return self.sharpe_ratio > 1.0 and self.tax_alpha_pct > 2.0


@dataclass
class WalkForwardResult:
    """Results from a single walk-forward fold."""

    fold_id: int
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    regression: RegressionMetrics
    directional: DirectionalMetrics
    overfitting_ratio: float  # test_mae / train_mae — ideally < 1.4


@dataclass
class ModelComparisonResult:
    """Aggregate comparison across all algorithm variants."""

    model_name: str
    walk_forward_results: List[WalkForwardResult] = field(default_factory=list)

    # Aggregated stats across folds
    mean_r2: float = 0.0
    std_r2: float = 0.0
    mean_da: float = 0.0
    std_da: float = 0.0
    mean_ic: float = 0.0
    mean_overfitting_ratio: float = 0.0

    def compute_aggregates(self) -> None:
        if not self.walk_forward_results:
            return
        r2s = [f.regression.r2 for f in self.walk_forward_results]
        das = [f.directional.directional_accuracy for f in self.walk_forward_results]
        ics = [f.regression.ic for f in self.walk_forward_results]
        ovs = [f.overfitting_ratio for f in self.walk_forward_results]
        self.mean_r2 = float(np.mean(r2s))
        self.std_r2 = float(np.std(r2s))
        self.mean_da = float(np.mean(das))
        self.std_da = float(np.std(das))
        self.mean_ic = float(np.mean(ics))
        self.mean_overfitting_ratio = float(np.mean(ovs))

    def summary(self) -> str:
        return (
            f"{self.model_name:30s} | "
            f"R²={self.mean_r2:.3f}±{self.std_r2:.3f} | "
            f"DA={self.mean_da:.3f}±{self.std_da:.3f} | "
            f"IC={self.mean_ic:.3f} | "
            f"Overfit={self.mean_overfitting_ratio:.2f}x"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Core metric calculators
# ─────────────────────────────────────────────────────────────────────────────


def compute_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    ic_window: int = 20,
) -> RegressionMetrics:
    """
    Compute full suite of regression metrics.

    Args:
        y_true:    Actual forward returns (e.g. 30-day returns, float array).
        y_pred:    Predicted forward returns (same shape).
        ic_window: Rolling window for ICIR computation.

    Returns:
        RegressionMetrics dataclass.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    y_true, y_pred = y_true[mask], y_pred[mask]

    n = len(y_true)
    if n < 10:
        raise ValueError(f"Not enough valid samples for metric computation: {n}")

    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = r2_score(y_true, y_pred)

    # MAPE — skip near-zero actuals to avoid division explosion
    nonzero = np.abs(y_true) > 1e-6
    mape = (
        float(
            np.mean(np.abs((y_true[nonzero] - y_pred[nonzero]) / y_true[nonzero])) * 100
        )
        if nonzero.sum() > 0
        else float("nan")
    )

    # Information Coefficient (IC) — Spearman rank correlation
    ic, _ = stats.spearmanr(y_true, y_pred)
    ic = float(ic) if np.isfinite(ic) else 0.0

    # ICIR — rolling IC stability (requires Series for rolling)
    if n >= ic_window * 2:
        s_true = pd.Series(y_true)
        s_pred = pd.Series(y_pred)
        rolling_ic = [
            stats.spearmanr(
                s_true.iloc[i : i + ic_window],
                s_pred.iloc[i : i + ic_window],
            )[0]
            for i in range(0, n - ic_window, ic_window // 2)
        ]
        rolling_ic = [x for x in rolling_ic if np.isfinite(x)]
        icir = (
            float(np.mean(rolling_ic) / (np.std(rolling_ic) + 1e-9))
            if rolling_ic
            else 0.0
        )
    else:
        icir = 0.0

    return RegressionMetrics(
        mae=float(mae),
        rmse=rmse,
        r2=float(r2),
        mape=mape,
        ic=ic,
        icir=icir,
        n_samples=n,
    )


def compute_directional_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    threshold: float = 0.0,
) -> DirectionalMetrics:
    """
    Convert continuous predictions to binary direction and compute signal quality.

    Args:
        y_true:    Actual returns.
        y_pred:    Predicted returns.
        threshold: Decision boundary — above = positive, below = negative.

    Returns:
        DirectionalMetrics dataclass.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    y_true, y_pred = y_true[mask], y_pred[mask]

    # Binary labels: 1 = positive return (buy), 0 = negative (sell/harvest)
    labels_true = (y_true > threshold).astype(int)
    labels_pred = (y_pred > threshold).astype(int)

    da = float(np.mean(labels_true == labels_pred))
    mcc = float(matthews_corrcoef(labels_true, labels_pred))

    # AUC-ROC — use raw predicted value as score
    try:
        # Shift to [0,1] probability-like range
        pred_scores = (y_pred - y_pred.min()) / ((y_pred.max() - y_pred.min()) + 1e-9)
        auc = float(roc_auc_score(labels_true, pred_scores))
    except ValueError:
        auc = 0.5

    # Per-class report for the HARVEST (negative return) class
    cm = confusion_matrix(labels_true, labels_pred)
    report = classification_report(
        labels_true, labels_pred, output_dict=True, zero_division=0
    )
    harvest_key = "0"  # class 0 = negative return = harvest candidate
    p = report.get(harvest_key, {}).get("precision", 0.0)
    r = report.get(harvest_key, {}).get("recall", 0.0)
    f1 = report.get(harvest_key, {}).get("f1-score", 0.0)

    return DirectionalMetrics(
        directional_accuracy=da,
        mcc=mcc,
        auc_roc=auc,
        precision_harvest=float(p),
        recall_harvest=float(r),
        f1_harvest=float(f1),
        confusion=cm,
    )


def compute_financial_metrics(
    portfolio_values: pd.Series,
    baseline_values: pd.Series,
    initial_capital: float,
    trades: List[Dict],
    risk_free_rate: float = 0.04,
) -> FinancialMetrics:
    """
    Compute Sharpe, Calmar, Drawdown, Tax Alpha from portfolio equity curves.

    Args:
        portfolio_values: Daily values of the active (harvesting) strategy.
        baseline_values:  Daily values of the buy-and-hold baseline.
        initial_capital:  Starting capital (denominator for Alpha).
        trades:           List of trade dicts with keys {tax_saved, pnl}.
        risk_free_rate:   Annual risk-free rate (default 4%).

    Returns:
        FinancialMetrics dataclass.
    """
    pv = portfolio_values.dropna()
    bv = baseline_values.dropna()

    # Daily returns
    daily_ret = pv.pct_change().dropna()
    n_days = len(daily_ret)
    years = n_days / 252.0

    ann_ret = float(((pv.iloc[-1] / pv.iloc[0]) ** (1 / max(years, 0.01))) - 1) * 100
    ann_vol = float(daily_ret.std() * np.sqrt(252)) * 100
    sharpe = float(((ann_ret / 100) - risk_free_rate) / max(ann_vol / 100, 1e-9))

    # Max drawdown
    rolling_max = pv.cummax()
    drawdowns = (pv - rolling_max) / rolling_max
    max_dd = float(drawdowns.min()) * 100

    calmar = float((ann_ret / 100) / max(abs(max_dd / 100), 1e-9))

    # Tax alpha
    tax_alpha = float((pv.iloc[-1] - bv.iloc[-1]) / initial_capital * 100)

    # Trade stats
    if trades:
        tax_savings = [t.get("tax_saved", 0) for t in trades]
        pnls = [t.get("pnl", 0) for t in trades]
        win_rate = float(np.mean([p > 0 for p in pnls])) if pnls else 0.0
        avg_tax = float(np.mean(tax_savings)) if tax_savings else 0.0
    else:
        win_rate, avg_tax = 0.0, 0.0

    return FinancialMetrics(
        tax_alpha_pct=tax_alpha,
        annualized_return_pct=ann_ret,
        annualized_vol_pct=ann_vol,
        sharpe_ratio=sharpe,
        max_drawdown_pct=max_dd,
        calmar_ratio=calmar,
        total_trades=len(trades),
        win_rate=win_rate,
        avg_tax_saved_per_trade=avg_tax,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Walk-Forward Cross-Validation
# ─────────────────────────────────────────────────────────────────────────────


class WalkForwardValidator:
    """
    Purged walk-forward cross-validation — the correct way to validate
    any time-series financial model.

    CRITICAL: Never use k-fold on time series — it leaks future data.
    Always train on past, test on unseen future.

    Parameters
    ----------
    n_splits:     Number of folds.
    train_size:   Fraction of total data for initial training window.
    test_size:    Fraction of each fold used as test (reanchored or expanding).
    gap:          Rows to skip between train end and test start.
                  Prevents lookahead from the feature computation window
                  (e.g. skip 30 rows if your target is 30-day forward return).
    expanding:    If True, training window grows each fold (expanding window).
                  If False, use a rolling (fixed-size) training window.
    """

    def __init__(
        self,
        n_splits: int = 5,
        train_size: float = 0.6,
        test_size: float = 0.1,
        gap: int = 30,
        expanding: bool = True,
    ):
        self.n_splits = n_splits
        self.train_size = train_size
        self.test_size = test_size
        self.gap = gap
        self.expanding = expanding

    def split(self, X: pd.DataFrame) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Yield (train_idx, test_idx) tuples.

        Args:
            X: Feature DataFrame with a DatetimeIndex.
        """
        n = len(X)
        initial_train = int(n * self.train_size)
        step = int(n * self.test_size)

        splits = []
        for fold in range(self.n_splits):
            test_start = initial_train + fold * step
            test_end = test_start + step

            if test_end > n:
                break

            train_end = test_start - self.gap
            train_start = 0 if self.expanding else max(0, train_end - initial_train)

            if train_end - train_start < 50:
                # Not enough training data for this fold — skip
                continue

            train_idx = np.arange(train_start, train_end)
            test_idx = np.arange(test_start, test_end)
            splits.append((train_idx, test_idx))

        return splits

    def evaluate_model(
        self,
        model,  # sklearn-compatible estimator
        X: pd.DataFrame,
        y: pd.Series,
        scaler=None,  # Optional: sklearn scaler fitted per fold
    ) -> List[WalkForwardResult]:
        """
        Run walk-forward validation and return per-fold results.

        Fits a fresh model on each training window to prevent lookahead.
        """
        from sklearn.preprocessing import StandardScaler

        results = []
        splits = self.split(X)

        for fold_id, (train_idx, test_idx) in enumerate(splits):
            X_train = X.iloc[train_idx]
            X_test = X.iloc[test_idx]
            y_train = y.iloc[train_idx]
            y_test = y.iloc[test_idx]

            # Fit scaler on training data only (critical — no test data leakage)
            sc = StandardScaler()
            X_train_sc = sc.fit_transform(X_train)
            X_test_sc = sc.transform(X_test)

            # Clone and fit model freshly for this fold
            from sklearn.base import clone as sklearn_clone

            try:
                fold_model = sklearn_clone(model)
            except Exception:
                fold_model = model  # fallback for non-sklearn estimators
            fold_model.fit(X_train_sc, y_train)

            # Predictions
            y_train_pred = fold_model.predict(X_train_sc)
            y_test_pred = fold_model.predict(X_test_sc)

            # Metrics
            train_reg = compute_regression_metrics(y_train.values, y_train_pred)
            test_reg = compute_regression_metrics(y_test.values, y_test_pred)
            test_dir = compute_directional_metrics(y_test.values, y_test_pred)

            overfitting_ratio = test_reg.mae / max(train_reg.mae, 1e-9)

            # Date labels
            dates = X.index
            result = WalkForwardResult(
                fold_id=fold_id,
                train_start=str(dates[train_idx[0]])[:10],
                train_end=str(dates[train_idx[-1]])[:10],
                test_start=str(dates[test_idx[0]])[:10],
                test_end=str(dates[test_idx[-1]])[:10],
                regression=test_reg,
                directional=test_dir,
                overfitting_ratio=overfitting_ratio,
            )
            results.append(result)

            print(
                f"  Fold {fold_id + 1}/{len(splits)} "
                f"[train {result.train_start}→{result.train_end} | "
                f"test {result.test_start}→{result.test_end}] "
                f"R²={test_reg.r2:.3f} DA={test_dir.directional_accuracy:.3f} "
                f"Overfit={overfitting_ratio:.2f}x"
            )

        return results


# ─────────────────────────────────────────────────────────────────────────────
# Statistical significance testing
# ─────────────────────────────────────────────────────────────────────────────


def compare_models_statistically(
    results_a: List[WalkForwardResult],
    results_b: List[WalkForwardResult],
    metric: str = "r2",
    alpha: float = 0.05,
) -> Dict:
    """
    Paired t-test comparing two models across walk-forward folds.

    This is what you cite in a research paper to show model A is
    *statistically* better than model B — not just lucky.

    Args:
        results_a:  Walk-forward results for model A.
        results_b:  Walk-forward results for model B.
        metric:     One of "r2", "mape", "da", "ic".
        alpha:      Significance threshold.

    Returns:
        Dict with t_stat, p_value, is_significant, effect_size (Cohen's d).
    """

    def _get_metric(results: List[WalkForwardResult], m: str) -> np.ndarray:
        if m == "r2":
            return np.array([r.regression.r2 for r in results])
        if m == "mape":
            return np.array([r.regression.mape for r in results])
        if m == "da":
            return np.array([r.directional.directional_accuracy for r in results])
        if m == "ic":
            return np.array([r.regression.ic for r in results])
        raise ValueError(f"Unknown metric: {m}")

    scores_a = _get_metric(results_a, metric)
    scores_b = _get_metric(results_b, metric)

    min_len = min(len(scores_a), len(scores_b))
    scores_a = scores_a[:min_len]
    scores_b = scores_b[:min_len]

    t_stat, p_val = stats.ttest_rel(scores_a, scores_b)
    diff = scores_a - scores_b
    effect_size = float(np.mean(diff) / (np.std(diff) + 1e-9))  # Cohen's d

    return {
        "metric": metric,
        "mean_a": float(np.mean(scores_a)),
        "mean_b": float(np.mean(scores_b)),
        "t_stat": float(t_stat),
        "p_value": float(p_val),
        "is_significant": bool(p_val < alpha),
        "effect_size_cohens_d": effect_size,
        "direction": "A > B" if np.mean(scores_a) > np.mean(scores_b) else "B > A",
    }


def diebold_mariano_test(
    y_true: np.ndarray,
    errors_a: np.ndarray,
    errors_b: np.ndarray,
) -> Dict:
    """
    Diebold-Mariano test — specifically designed for forecast comparison.
    Preferred over t-test for financial time series.

    Null hypothesis: equal forecast accuracy.
    Reject → one model is statistically better.
    """
    d = errors_a**2 - errors_b**2  # loss differential (MSE-based)
    n = len(d)
    d_mean = np.mean(d)

    # Newey-West HAC variance to handle autocorrelation in d
    lags = int(np.floor(4 * (n / 100) ** (2 / 9)))
    gamma_0 = np.var(d, ddof=1)
    gamma_k = sum(
        (1 - k / (lags + 1)) * np.cov(d[k:], d[:-k])[0, 1]
        for k in range(1, lags + 1)
        if len(d[k:]) > 1
    )
    hac_var = (gamma_0 + 2 * gamma_k) / n
    dm_stat = d_mean / max(np.sqrt(hac_var), 1e-12)
    p_value = 2 * (1 - stats.norm.cdf(abs(dm_stat)))

    return {
        "dm_statistic": float(dm_stat),
        "p_value": float(p_value),
        "is_significant": bool(p_value < 0.05),
        "preferred_model": "A" if dm_stat < 0 else "B",
    }


# ─────────────────────────────────────────────────────────────────────────────
# SHAP feature importance (optional — requires: pip install shap)
# ─────────────────────────────────────────────────────────────────────────────


def compute_shap_importance(
    model,
    X_test: pd.DataFrame,
    max_samples: int = 200,
) -> Optional[pd.DataFrame]:
    """
    Compute SHAP values for feature importance and stability analysis.

    Returns a DataFrame of mean |SHAP| per feature, sorted descending.
    Returns None if shap is not installed.
    """
    try:
        import shap  # type: ignore
    except ImportError:
        print("⚠️  shap not installed — skipping SHAP analysis. Run: pip install shap")
        return None

    sample = X_test.sample(min(max_samples, len(X_test)), random_state=42)

    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(sample)
    except Exception:
        explainer = shap.KernelExplainer(model.predict, sample)
        shap_values = explainer.shap_values(sample, nsamples=50)

    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    importance = pd.DataFrame(
        {
            "feature": X_test.columns,
            "mean_abs_shap": np.abs(shap_values).mean(axis=0),
        }
    ).sort_values("mean_abs_shap", ascending=False)

    return importance


# ─────────────────────────────────────────────────────────────────────────────
# Report builder
# ─────────────────────────────────────────────────────────────────────────────


def print_comparison_table(model_results: List[ModelComparisonResult]) -> None:
    """Print a formatted comparison table suitable for a paper appendix."""
    print("\n" + "=" * 90)
    print(
        f"{'MODEL':30s} | {'R² (mean±std)':20s} | {'DA (mean±std)':20s} | {'IC':8s} | {'Overfit':8s}"
    )
    print("-" * 90)
    for r in sorted(model_results, key=lambda x: x.mean_r2, reverse=True):
        print(r.summary())
    print("=" * 90)
    print("Thresholds for publishable result: R² > 0.30, DA > 0.55, Overfit < 1.40")
    print()


class FinancialEvaluator:
    """Wrapper class providing validation helper methods for model evaluation."""

    @staticmethod
    def evaluate_statistical_errors(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
        """Computes basic statistical metrics (RMSE, etc.) for models.py compatibility."""
        metrics = compute_regression_metrics(y_true, y_pred)
        return {
            "RMSE": metrics.rmse,
            "MAE": metrics.mae,
            "R2": metrics.r2,
            "MAPE": metrics.mape
        }

    @staticmethod
    def calculate_directional_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Computes directional accuracy percentage (0-100) for models.py compatibility."""
        metrics = compute_directional_metrics(y_true, y_pred)
        return metrics.directional_accuracy * 100


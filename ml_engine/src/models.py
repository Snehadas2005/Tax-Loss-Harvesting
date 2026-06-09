import os
import pickle
from typing import Tuple, Any
from .clustering import TaxLossClusterer as GMMClusterer
from .prediction import TaxLossPredictor as QuantilePredictor

# If you kept your original components for a baseline run, import them here
# from sklearn.cluster import KMeans
# from sklearn.linear_model import LinearRegression


class ModelPipelineFactory:
    """Factory to generate pipeline variations for terminal benchmarking."""

    @staticmethod
    def build_combination(name: str, config: dict = None) -> Tuple[Any, Any]:
        config = config or {}
        name = name.upper()

        if name == "BASELINE":
            # Reconstruct original Baseline combinations (e.g., KMeans + Regressor)
            from sklearn.cluster import KMeans
            from sklearn.linear_model import LinearRegression

            clusterer = KMeans(n_clusters=config.get("n_clusters", 5), random_state=42)
            predictor = LinearRegression()
            return clusterer, predictor

        elif name == "COMBINATION_A":
            from sklearn.cluster import OPTICS
            import xgboost as xgb

            clusterer = OPTICS(min_samples=2, xi=0.05, metric="cosine", n_jobs=-1)
            predictor = xgb.XGBRegressor(
                n_estimators=100, max_depth=4, objective="reg:squarederror"
            )
            return clusterer, predictor

        elif name == "COMBINATION_B":
            # Our champion model: GMM + Multi-Quantile Forest
            clusterer = GMMClusterer(
                **config.get(
                    "clustering", {"n_components": 5, "covariance_type": "full"}
                )
            )
            predictor = QuantilePredictor(
                **config.get("prediction", {"n_estimators": 100, "max_depth": 5})
            )
            return clusterer, predictor

        else:
            raise ValueError(f"Unknown combination profile name: {name}")


def save_production_pipeline(clusterer: Any, predictor: Any, save_dir: str = "models"):
    """Serializes the selected model combination to production paths used by the frontend api."""
    os.makedirs(save_dir, exist_ok=True)
    with open(os.path.join(save_dir, "clusterer.pkl"), "wb") as f:
        pickle.dump(clusterer, f)
    with open(os.path.join(save_dir, "predictor.pkl"), "wb") as f:
        pickle.dump(predictor, f)


def load_pipeline(save_dir: str = "models") -> Tuple[Any, Any]:
    """Loads the active production models."""
    with open(os.path.join(save_dir, "clusterer.pkl"), "rb") as f:
        clusterer = pickle.load(f)
    with open(os.path.join(save_dir, "predictor.pkl"), "rb") as f:
        predictor = pickle.load(f)
    return clusterer, predictor

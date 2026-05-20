# ml_engine/src/__init__.py

from src.processor import DataProcessor
from src.clustering import PortfolioClusterer
from src.prediction import TrendPredictor
from src.backtester import TaxBacktester

# This exposes your main classes directly when someone imports the src package
__all__ = [
    "DataProcessor",
    "PortfolioClusterer",
    "TrendPredictor",
    "TaxBacktester"
]
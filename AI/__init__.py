"""
Advanced AI System for Real Estate Analysis Platform

This package provides comprehensive AI capabilities including:
- Price prediction using ensemble methods
- Demand analysis with time series forecasting  
- Recommendation systems with collaborative and content-based filtering
- Market analysis and trend prediction

Senior-level implementation with TensorFlow, PyTorch, HuggingFace Transformers,
MLflow for experiment tracking, and Kubeflow for ML pipelines.
"""

from .config import ai_config, model_configs
from .core import DataProcessor
from .models import (
    # Price Prediction
    PricePredictionPipeline,
    EnsemblePriceModel,
    XGBoostPriceModel,
    LightGBMPriceModel,
    # TensorFlowPriceModel,  # Disabled for Python 3.13 compatibility
    PyTorchPriceModel,
    
    # Demand Analysis
    DemandAnalysisPipeline,
    DemandAnalyzer,
    ProphetDemandModel,
    LSTMDemandModel,
    EnsembleDemandModel,
    
    # Recommendation System
    RecommendationPipeline,
    HybridRecommender,
    CollaborativeFilteringRecommender,
    ContentBasedRecommender,
    DeepLearningRecommender,
    RecommendationExplainer
)

__version__ = "1.0.0"
__author__ = "Кириешки"

__all__ = [
    # Configuration
    "ai_config",
    "model_configs",
    
    # Core
    "DataProcessor",
    
    # Price Prediction
    "PricePredictionPipeline",
    "EnsemblePriceModel",
    "XGBoostPriceModel",
    "LightGBMPriceModel", 
    # "TensorFlowPriceModel",  # Disabled for Python 3.13 compatibility
    "PyTorchPriceModel",
    
    # Demand Analysis
    "DemandAnalysisPipeline",
    "DemandAnalyzer",
    "ProphetDemandModel",
    "LSTMDemandModel",
    "EnsembleDemandModel",
    
    # Recommendation System
    "RecommendationPipeline",
    "HybridRecommender",
    "CollaborativeFilteringRecommender",
    "ContentBasedRecommender",
    "DeepLearningRecommender",
    "RecommendationExplainer"
]

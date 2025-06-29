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

# Configuration imports with fallback
try:
    from .config import ai_config, model_configs
except ImportError as e:
    print(f"AI config not available: {e}")
    ai_config = None
    model_configs = None

# Core imports with fallback
try:
    from .core import DataProcessor
except ImportError as e:
    print(f"AI core not available: {e}")
    class DataProcessor:
        def __init__(self, *args, **kwargs):
            raise ImportError("Data processor not available")

# Model imports with fallback
try:
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
except ImportError as e:
    print(f"AI models not available: {e}")
    
    # Fallback classes for all models
    class PricePredictionPipeline:
        def __init__(self, *args, **kwargs):
            raise ImportError("Price prediction pipeline not available")
    
    class EnsemblePriceModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("Ensemble price model not available")
    
    class XGBoostPriceModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("XGBoost price model not available")
    
    class LightGBMPriceModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("LightGBM price model not available")
    
    class PyTorchPriceModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch price model not available")
    
    class DemandAnalysisPipeline:
        def __init__(self, *args, **kwargs):
            raise ImportError("Demand analysis pipeline not available")
    
    class DemandAnalyzer:
        def __init__(self, *args, **kwargs):
            raise ImportError("Demand analyzer not available")
    
    class ProphetDemandModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("Prophet demand model not available")
    
    class LSTMDemandModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("LSTM demand model not available")
    
    class EnsembleDemandModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("Ensemble demand model not available")
    
    class RecommendationPipeline:
        def __init__(self, *args, **kwargs):
            raise ImportError("Recommendation pipeline not available")
    
    class HybridRecommender:
        def __init__(self, *args, **kwargs):
            raise ImportError("Hybrid recommender not available")
    
    class CollaborativeFilteringRecommender:
        def __init__(self, *args, **kwargs):
            raise ImportError("Collaborative filtering recommender not available")
    
    class ContentBasedRecommender:
        def __init__(self, *args, **kwargs):
            raise ImportError("Content-based recommender not available")
    
    class DeepLearningRecommender:
        def __init__(self, *args, **kwargs):
            raise ImportError("Deep learning recommender not available")
    
    class RecommendationExplainer:
        def __init__(self, *args, **kwargs):
            raise ImportError("Recommendation explainer not available")

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

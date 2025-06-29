"""
AI Core Module for Real Estate Analysis Platform
"""

try:
    from .data_processing import (
        DataProcessor,
        DataProcessingConfig,
        MissingValueHandler,
        OutlierDetector,
        FeatureEngineer
    )
except ImportError as e:
    print(f"Data processing module not available: {e}")
    
    class DataProcessor:
        def __init__(self, *args, **kwargs):
            raise ImportError("Data processor not available")
    
    class DataProcessingConfig:
        def __init__(self, *args, **kwargs):
            raise ImportError("Data processing config not available")
    
    class MissingValueHandler:
        def __init__(self, *args, **kwargs):
            raise ImportError("Missing value handler not available")
    
    class OutlierDetector:
        def __init__(self, *args, **kwargs):
            raise ImportError("Outlier detector not available")
    
    class FeatureEngineer:
        def __init__(self, *args, **kwargs):
            raise ImportError("Feature engineer not available")

__all__ = [
    "DataProcessor",
    "DataProcessingConfig", 
    "MissingValueHandler",
    "OutlierDetector",
    "FeatureEngineer"
]

"""
AI Configuration for Real Estate Analysis Platform
Senior-level configuration with comprehensive settings for all AI services.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseSettings, Field
from enum import Enum


class ModelType(str, Enum):
    """AI Model Types"""
    PRICE_PREDICTION = "price_prediction"
    DEMAND_ANALYSIS = "demand_analysis"
    RECOMMENDATION = "recommendation"
    MARKET_ANALYSIS = "market_analysis"
    TEXT_ANALYSIS = "text_analysis"
    IMAGE_ANALYSIS = "image_analysis"
    TIME_SERIES = "time_series"


class Environment(str, Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class AIConfig(BaseSettings):
    """Main AI Configuration Class"""
    
    # Environment settings
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="AI_ENVIRONMENT")
    debug: bool = Field(default=True, env="AI_DEBUG")
    
    # Base paths
    ai_base_path: Path = Field(default=Path(__file__).parent, env="AI_BASE_PATH")
    models_path: Path = Field(default=None, env="AI_MODELS_PATH")
    data_path: Path = Field(default=None, env="AI_DATA_PATH")
    logs_path: Path = Field(default=None, env="AI_LOGS_PATH")
    
    # MLflow settings
    mlflow_tracking_uri: str = Field(default="sqlite:///mlflow.db", env="MLFLOW_TRACKING_URI")
    mlflow_experiment_name: str = Field(default="real_estate_ai", env="MLFLOW_EXPERIMENT_NAME")
    mlflow_model_registry_uri: str = Field(default=None, env="MLFLOW_MODEL_REGISTRY_URI")
    
    # Kubeflow settings
    kubeflow_host: str = Field(default="http://localhost:8080", env="KUBEFLOW_HOST")
    kubeflow_namespace: str = Field(default="kubeflow", env="KUBEFLOW_NAMESPACE")
    kubeflow_service_account: str = Field(default="pipeline-runner", env="KUBEFLOW_SERVICE_ACCOUNT")
    
    # Model serving settings
    model_serving_host: str = Field(default="0.0.0.0", env="MODEL_SERVING_HOST")
    model_serving_port: int = Field(default=8001, env="MODEL_SERVING_PORT")
    model_serving_workers: int = Field(default=4, env="MODEL_SERVING_WORKERS")
    
    # Redis settings for caching
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=1, env="REDIS_AI_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Database settings
    database_url: str = Field(default="postgresql://user:pass@localhost/realestate", env="DATABASE_URL")
    
    # GPU settings
    use_gpu: bool = Field(default=True, env="AI_USE_GPU")
    gpu_memory_growth: bool = Field(default=True, env="AI_GPU_MEMORY_GROWTH")
    mixed_precision: bool = Field(default=True, env="AI_MIXED_PRECISION")
    
    # Model training settings
    batch_size: int = Field(default=32, env="AI_BATCH_SIZE")
    max_epochs: int = Field(default=100, env="AI_MAX_EPOCHS")
    learning_rate: float = Field(default=0.001, env="AI_LEARNING_RATE")
    early_stopping_patience: int = Field(default=10, env="AI_EARLY_STOPPING_PATIENCE")
    
    # Hyperparameter optimization
    optuna_n_trials: int = Field(default=100, env="AI_OPTUNA_N_TRIALS")
    optuna_sampler: str = Field(default="TPE", env="AI_OPTUNA_SAMPLER")
    
    # Data processing settings
    data_validation_split: float = Field(default=0.2, env="AI_VALIDATION_SPLIT")
    data_test_split: float = Field(default=0.1, env="AI_TEST_SPLIT")
    data_random_seed: int = Field(default=42, env="AI_RANDOM_SEED")
    
    # Feature engineering
    max_categorical_cardinality: int = Field(default=50, env="AI_MAX_CATEGORICAL_CARDINALITY")
    missing_value_threshold: float = Field(default=0.3, env="AI_MISSING_VALUE_THRESHOLD")
    correlation_threshold: float = Field(default=0.95, env="AI_CORRELATION_THRESHOLD")
    
    # HuggingFace settings
    hf_model_cache_dir: Optional[str] = Field(default=None, env="HF_MODEL_CACHE_DIR")
    hf_token: Optional[str] = Field(default=None, env="HF_TOKEN")
    
    # Monitoring and logging
    log_level: str = Field(default="INFO", env="AI_LOG_LEVEL")
    enable_tensorboard: bool = Field(default=True, env="AI_ENABLE_TENSORBOARD")
    enable_wandb: bool = Field(default=False, env="AI_ENABLE_WANDB")
    wandb_project: str = Field(default="real-estate-ai", env="WANDB_PROJECT")
    wandb_entity: Optional[str] = Field(default=None, env="WANDB_ENTITY")
    
    # API settings
    api_rate_limit: int = Field(default=100, env="AI_API_RATE_LIMIT")
    api_timeout: int = Field(default=30, env="AI_API_TIMEOUT")
    
    # Security
    model_encryption_key: Optional[str] = Field(default=None, env="AI_MODEL_ENCRYPTION_KEY")
    enable_model_validation: bool = Field(default=True, env="AI_ENABLE_MODEL_VALIDATION")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_paths()
    
    def _setup_paths(self):
        """Setup default paths if not provided"""
        if self.models_path is None:
            self.models_path = self.ai_base_path / "models"
        if self.data_path is None:
            self.data_path = self.ai_base_path / "data"
        if self.logs_path is None:
            self.logs_path = self.ai_base_path / "logs"
        
        # Create directories if they don't exist
        for path in [self.models_path, self.data_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)


class ModelConfigs:
    """Model-specific configurations"""
    
    PRICE_PREDICTION = {
        "model_type": "ensemble",
        "base_models": ["xgboost", "lightgbm", "neural_network"],
        "features": [
            "area", "kitchen_area", "rooms", "level", "levels", 
            "geo_lat", "geo_lon", "building_type", "object_type",
            "postal_code", "street_id", "id_region", "house_id"
        ],
        "target": "price",
        "preprocessing": {
            "normalize_features": True,
            "handle_missing": "median",
            "encode_categorical": "target_encoding",
            "outlier_detection": "isolation_forest"
        },
        "hyperparameters": {
            "xgboost": {
                "n_estimators": [100, 200, 300],
                "max_depth": [3, 6, 9],
                "learning_rate": [0.01, 0.1, 0.2],
                "subsample": [0.8, 0.9, 1.0]
            },
            "lightgbm": {
                "n_estimators": [100, 200, 300],
                "max_depth": [3, 6, 9],
                "learning_rate": [0.01, 0.1, 0.2],
                "feature_fraction": [0.8, 0.9, 1.0]
            },
            "neural_network": {
                "hidden_layers": [[128, 64], [256, 128, 64], [512, 256, 128]],
                "dropout": [0.2, 0.3, 0.4],
                "batch_size": [32, 64, 128],
                "learning_rate": [0.001, 0.01, 0.1]
            }
        }
    }
    
    DEMAND_ANALYSIS = {
        "model_type": "time_series_ensemble",
        "base_models": ["prophet", "lstm", "transformer"],
        "features": [
            "search_volume", "view_count", "contact_count", 
            "price_changes", "seasonal_indicators", "economic_indicators"
        ],
        "target": "demand_score",
        "time_features": ["hour", "day_of_week", "month", "quarter", "is_holiday"],
        "lookback_window": 90,
        "forecast_horizon": 30
    }
    
    RECOMMENDATION = {
        "model_type": "hybrid",
        "components": ["collaborative_filtering", "content_based", "deep_learning"],
        "embedding_dim": 128,
        "user_features": [
            "search_history", "view_history", "budget_range", 
            "preferred_regions", "lifestyle_preferences"
        ],
        "item_features": [
            "price", "area", "rooms", "location_features", 
            "amenities", "building_features"
        ],
        "negative_sampling_ratio": 5,
        "regularization": 0.01
    }
    
    MARKET_ANALYSIS = {
        "model_type": "multi_task",
        "tasks": ["price_trend", "volume_trend", "sentiment_analysis"],
        "features": [
            "historical_prices", "transaction_volumes", "inventory_levels",
            "economic_indicators", "demographic_data", "news_sentiment"
        ],
        "time_aggregations": ["daily", "weekly", "monthly"],
        "spatial_aggregations": ["district", "city", "region"]
    }
    
    TEXT_ANALYSIS = {
        "model_type": "transformer",
        "base_model": "bert-base-multilingual-cased",
        "tasks": ["sentiment", "entity_extraction", "classification"],
        "max_length": 512,
        "fine_tuning": {
            "learning_rate": 2e-5,
            "batch_size": 16,
            "epochs": 3,
            "warmup_steps": 500
        }
    }
    
    IMAGE_ANALYSIS = {
        "model_type": "vision_transformer",
        "base_model": "microsoft/swin-base-patch4-window7-224",
        "tasks": ["room_classification", "quality_assessment", "feature_extraction"],
        "image_size": (224, 224),
        "augmentations": [
            "horizontal_flip", "rotation", "brightness", "contrast"
        ],
        "transfer_learning": {
            "freeze_backbone": True,
            "learning_rate": 1e-4,
            "batch_size": 32
        }
    }


# Global configuration instance
ai_config = AIConfig()

# Model configurations
model_configs = ModelConfigs()

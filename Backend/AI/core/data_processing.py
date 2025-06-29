"""
Advanced Data Processing and Feature Engineering for Real Estate AI
Senior-level implementation with comprehensive preprocessing capabilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
import geopy.distance
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

try:
    from config import ai_config
except ImportError:
    # Fallback for direct execution
    ai_config = type('Config', (), {'data_random_seed': 42})()


@dataclass
class DataProcessingConfig:
    """Configuration for data processing pipeline"""
    missing_threshold: float = 0.3
    correlation_threshold: float = 0.95
    outlier_threshold: float = 0.1
    categorical_threshold: int = 50
    test_size: float = 0.2
    validation_size: float = 0.1
    random_state: int = 42


class BaseProcessor(ABC):
    """Abstract base class for data processors"""
    
    def __init__(self, config: DataProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_fitted = False
    
    @abstractmethod
    def fit(self, data: pd.DataFrame) -> 'BaseProcessor':
        """Fit the processor to data"""
        pass
    
    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform data using fitted processor"""
        pass
    
    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fit and transform data in one step"""
        return self.fit(data).transform(data)


class MissingValueHandler(BaseProcessor):
    """Advanced missing value handling with multiple strategies"""
    
    def __init__(self, config: DataProcessingConfig, strategy: str = "smart"):
        super().__init__(config)
        self.strategy = strategy
        self.imputers = {}
        self.drop_columns = []
    
    def fit(self, data: pd.DataFrame) -> 'MissingValueHandler':
        """Fit missing value handling strategies"""
        self.logger.info("Fitting missing value handler...")
        
        # Identify columns to drop (too many missing values)
        missing_ratios = data.isnull().sum() / len(data)
        self.drop_columns = missing_ratios[missing_ratios > self.config.missing_threshold].index.tolist()
        
        # Fit imputers for remaining columns
        remaining_data = data.drop(columns=self.drop_columns)
        
        for column in remaining_data.columns:
            if remaining_data[column].isnull().sum() == 0:
                continue
                
            if remaining_data[column].dtype in ['object', 'category']:
                # Categorical columns
                self.imputers[column] = SimpleImputer(strategy='most_frequent')
            elif column in ['geo_lat', 'geo_lon']:
                # Geographic coordinates - use KNN
                self.imputers[column] = KNNImputer(n_neighbors=5)
            elif column in ['price', 'area', 'kitchen_area']:
                # Important numerical columns - use median
                self.imputers[column] = SimpleImputer(strategy='median')
            else:
                # Other numerical columns - use mean
                self.imputers[column] = SimpleImputer(strategy='mean')
            
            # Fit the imputer
            self.imputers[column].fit(remaining_data[[column]])
        
        self.is_fitted = True
        self.logger.info(f"Fitted missing value handler. Dropping {len(self.drop_columns)} columns.")
        return self
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform data by handling missing values"""
        if not self.is_fitted:
            raise ValueError("Handler must be fitted before transform")
        
        # Drop columns with too many missing values
        transformed_data = data.drop(columns=self.drop_columns, errors='ignore')
        
        # Apply imputers
        for column, imputer in self.imputers.items():
            if column in transformed_data.columns:
                transformed_data[column] = imputer.transform(transformed_data[[column]]).ravel()
        
        return transformed_data


class OutlierDetector(BaseProcessor):
    """Multi-method outlier detection and handling"""
    
    def __init__(self, config: DataProcessingConfig, method: str = "isolation_forest"):
        super().__init__(config)
        self.method = method
        self.outlier_detectors = {}
        self.outlier_bounds = {}
    
    def fit(self, data: pd.DataFrame) -> 'OutlierDetector':
        """Fit outlier detection models"""
        self.logger.info(f"Fitting outlier detector using {self.method}...")
        
        numerical_columns = data.select_dtypes(include=[np.number]).columns
        
        for column in numerical_columns:
            if column in ['geo_lat', 'geo_lon']:
                # Geographic coordinates - use IQR method
                Q1 = data[column].quantile(0.25)
                Q3 = data[column].quantile(0.75)
                IQR = Q3 - Q1
                self.outlier_bounds[column] = {
                    'lower': Q1 - 1.5 * IQR,
                    'upper': Q3 + 1.5 * IQR
                }
            elif column == 'price':
                # Price - use log-normal distribution approach
                log_prices = np.log1p(data[column].dropna())
                mean_log = log_prices.mean()
                std_log = log_prices.std()
                self.outlier_bounds[column] = {
                    'lower': np.expm1(mean_log - 3 * std_log),
                    'upper': np.expm1(mean_log + 3 * std_log)
                }
            else:
                # Other numerical columns - use Isolation Forest
                if self.method == "isolation_forest":
                    detector = IsolationForest(
                        contamination=self.config.outlier_threshold,
                        random_state=self.config.random_state
                    )
                    detector.fit(data[[column]].dropna())
                    self.outlier_detectors[column] = detector
        
        self.is_fitted = True
        return self
    
    def transform(self, data: pd.DataFrame, action: str = "clip") -> pd.DataFrame:
        """Transform data by handling outliers"""
        if not self.is_fitted:
            raise ValueError("Detector must be fitted before transform")
        
        transformed_data = data.copy()
        
        # Handle outliers based on bounds
        for column, bounds in self.outlier_bounds.items():
            if column in transformed_data.columns:
                if action == "clip":
                    transformed_data[column] = transformed_data[column].clip(
                        lower=bounds['lower'], upper=bounds['upper']
                    )
                elif action == "remove":
                    mask = (
                        (transformed_data[column] >= bounds['lower']) & 
                        (transformed_data[column] <= bounds['upper'])
                    )
                    transformed_data = transformed_data[mask]
        
        # Handle outliers using fitted detectors
        for column, detector in self.outlier_detectors.items():
            if column in transformed_data.columns:
                outlier_mask = detector.predict(transformed_data[[column]]) == -1
                if action == "clip":
                    # Replace outliers with median
                    median_value = transformed_data[column].median()
                    transformed_data.loc[outlier_mask, column] = median_value
                elif action == "remove":
                    transformed_data = transformed_data[~outlier_mask]
        
        return transformed_data


class FeatureEngineer:
    """Advanced feature engineering for real estate data"""
    
    def __init__(self, config: DataProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.scalers = {}
        self.encoders = {}
        self.feature_names = []
    
    def create_geographic_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create geographic and location-based features"""
        self.logger.info("Creating geographic features...")
        
        df = data.copy()
        
        # City center coordinates (Moscow as default)
        city_center_lat, city_center_lon = 55.7558, 37.6176
        
        # Distance from city center
        if 'geo_lat' in df.columns and 'geo_lon' in df.columns:
            df['distance_to_center'] = df.apply(
                lambda row: geopy.distance.geodesic(
                    (row['geo_lat'], row['geo_lon']),
                    (city_center_lat, city_center_lon)
                ).kilometers if pd.notna(row['geo_lat']) and pd.notna(row['geo_lon']) else np.nan,
                axis=1
            )
            
            # Geographic clusters (using k-means on lat/lon)
            if not df[['geo_lat', 'geo_lon']].isnull().all().any():
                from sklearn.cluster import KMeans
                kmeans = KMeans(n_clusters=10, random_state=self.config.random_state)
                valid_coords = df[['geo_lat', 'geo_lon']].dropna()
                if len(valid_coords) > 0:
                    clusters = kmeans.fit_predict(valid_coords)
                    df.loc[valid_coords.index, 'geo_cluster'] = clusters
        
        return df
    
    def create_building_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create building and property features"""
        self.logger.info("Creating building features...")
        
        df = data.copy()
        
        # Floor position features
        if 'level' in df.columns and 'levels' in df.columns:
            df['floor_ratio'] = df['level'] / df['levels']
            df['is_first_floor'] = (df['level'] == 1).astype(int)
            df['is_last_floor'] = (df['level'] == df['levels']).astype(int)
            df['is_middle_floor'] = (
                (df['level'] > 1) & (df['level'] < df['levels'])
            ).astype(int)
        
        # Area features
        if 'area' in df.columns and 'kitchen_area' in df.columns:
            df['kitchen_ratio'] = df['kitchen_area'] / df['area']
            df['living_area'] = df['area'] - df['kitchen_area']
            df['area_per_room'] = df['area'] / df['rooms'].replace(0, 1)
        
        # Room features
        if 'rooms' in df.columns:
            df['is_studio'] = (df['rooms'] == -1).astype(int)
            df['room_category'] = pd.cut(
                df['rooms'].replace(-1, 0), 
                bins=[-1, 0, 1, 2, 3, 5, 10], 
                labels=['studio', '1room', '2room', '3room', '4-5room', '6+room']
            )
        
        # Building type features
        if 'building_type' in df.columns:
            building_quality_map = {0: 0, 1: 1, 2: 2, 3: 4, 4: 5, 5: 3, 6: 1}
            df['building_quality'] = df['building_type'].map(building_quality_map)
        
        return df
    
    def create_market_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create market and economic features"""
        self.logger.info("Creating market features...")
        
        df = data.copy()
        
        # Price per square meter
        if 'price' in df.columns and 'area' in df.columns:
            df['price_per_sqm'] = df['price'] / df['area']
        
        # Regional price statistics
        if 'id_region' in df.columns and 'price' in df.columns:
            region_stats = df.groupby('id_region')['price'].agg(['mean', 'median', 'std'])
            df = df.merge(
                region_stats.add_prefix('region_price_'), 
                left_on='id_region', 
                right_index=True, 
                how='left'
            )
            
            # Price relative to regional average
            df['price_vs_region'] = df['price'] / df['region_price_mean']
        
        # Street-level statistics
        if 'street_id' in df.columns and 'price' in df.columns:
            street_stats = df.groupby('street_id')['price'].agg(['mean', 'count'])
            df = df.merge(
                street_stats.add_prefix('street_'), 
                left_on='street_id', 
                right_index=True, 
                how='left'
            )
        
        return df
    
    def create_temporal_features(self, data: pd.DataFrame, date_column: str = None) -> pd.DataFrame:
        """Create temporal features if date information is available"""
        if date_column and date_column in data.columns:
            self.logger.info("Creating temporal features...")
            
            df = data.copy()
            df[date_column] = pd.to_datetime(df[date_column])
            
            df['year'] = df[date_column].dt.year
            df['month'] = df[date_column].dt.month
            df['quarter'] = df[date_column].dt.quarter
            df['day_of_year'] = df[date_column].dt.dayofyear
            df['is_weekend'] = df[date_column].dt.weekday.isin([5, 6]).astype(int)
            
            # Market seasonality
            df['season'] = df['month'].map({
                12: 'winter', 1: 'winter', 2: 'winter',
                3: 'spring', 4: 'spring', 5: 'spring',
                6: 'summer', 7: 'summer', 8: 'summer',
                9: 'autumn', 10: 'autumn', 11: 'autumn'
            })
            
            return df
        
        return data
    
    def encode_categorical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features using various strategies"""
        self.logger.info("Encoding categorical features...")
        
        df = data.copy()
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        
        for column in categorical_columns:
            unique_values = df[column].nunique()
            
            if unique_values <= 10:
                # One-hot encoding for low cardinality
                encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
                encoded = encoder.fit_transform(df[[column]])
                encoded_df = pd.DataFrame(
                    encoded, 
                    columns=[f"{column}_{cat}" for cat in encoder.categories_[0]],
                    index=df.index
                )
                df = pd.concat([df.drop(columns=[column]), encoded_df], axis=1)
                self.encoders[column] = encoder
            
            elif unique_values <= self.config.categorical_threshold:
                # Label encoding for medium cardinality
                encoder = LabelEncoder()
                df[f"{column}_encoded"] = encoder.fit_transform(df[column].fillna('unknown'))
                self.encoders[column] = encoder
            
            else:
                # Target encoding for high cardinality (if target is available)
                # For now, just drop or use frequency encoding
                df[f"{column}_frequency"] = df[column].map(df[column].value_counts())
                df = df.drop(columns=[column])
        
        return df
    
    def scale_features(self, data: pd.DataFrame, method: str = "robust") -> pd.DataFrame:
        """Scale numerical features"""
        self.logger.info(f"Scaling features using {method} scaler...")
        
        df = data.copy()
        numerical_columns = df.select_dtypes(include=[np.number]).columns
        
        if method == "standard":
            scaler = StandardScaler()
        elif method == "robust":
            scaler = RobustScaler()
        else:
            raise ValueError(f"Unknown scaling method: {method}")
        
        df[numerical_columns] = scaler.fit_transform(df[numerical_columns])
        self.scalers[method] = scaler
        
        return df


class DataProcessor:
    """Main data processing pipeline coordinator"""
    
    def __init__(self, config: Optional[DataProcessingConfig] = None):
        self.config = config or DataProcessingConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize processors
        self.missing_handler = MissingValueHandler(self.config)
        self.outlier_detector = OutlierDetector(self.config)
        self.feature_engineer = FeatureEngineer(self.config)
        
        self.is_fitted = False
        self.feature_names = []
    
    def fit(self, data: pd.DataFrame, target_column: str = 'price') -> 'DataProcessor':
        """Fit the entire processing pipeline"""
        self.logger.info("Fitting data processing pipeline...")
        
        # Store target column
        self.target_column = target_column
        
        # Fit processors in sequence
        cleaned_data = self.missing_handler.fit_transform(data)
        cleaned_data = self.outlier_detector.fit_transform(cleaned_data)
        
        # Feature engineering
        engineered_data = self.feature_engineer.create_geographic_features(cleaned_data)
        engineered_data = self.feature_engineer.create_building_features(engineered_data)
        engineered_data = self.feature_engineer.create_market_features(engineered_data)
        
        # Encoding and scaling
        encoded_data = self.feature_engineer.encode_categorical_features(engineered_data)
        
        self.feature_names = encoded_data.columns.tolist()
        self.is_fitted = True
        
        self.logger.info(f"Data processing pipeline fitted with {len(self.feature_names)} features")
        return self
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform data using fitted pipeline"""
        if not self.is_fitted:
            raise ValueError("Pipeline must be fitted before transform")
        
        # Apply transformations in sequence
        cleaned_data = self.missing_handler.transform(data)
        cleaned_data = self.outlier_detector.transform(cleaned_data)
        
        # Feature engineering
        engineered_data = self.feature_engineer.create_geographic_features(cleaned_data)
        engineered_data = self.feature_engineer.create_building_features(engineered_data)
        engineered_data = self.feature_engineer.create_market_features(engineered_data)
        
        # Encoding
        encoded_data = self.feature_engineer.encode_categorical_features(engineered_data)
        
        # Ensure same features as training
        for feature in self.feature_names:
            if feature not in encoded_data.columns:
                encoded_data[feature] = 0
        
        return encoded_data[self.feature_names]
    
    def prepare_train_test_split(
        self, 
        data: pd.DataFrame, 
        target_column: str = 'price'
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Prepare train-test split with proper preprocessing"""
        
        # Separate features and target
        X = data.drop(columns=[target_column])
        y = data[target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=self.config.test_size,
            random_state=self.config.random_state,
            stratify=None  # Can add stratification for categorical targets
        )
        
        # Fit and transform
        self.fit(X_train, target_column)
        X_train_processed = self.transform(X_train)
        X_test_processed = self.transform(X_test)
        
        return X_train_processed, X_test_processed, y_train, y_test
    
    def get_feature_importance_data(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """Calculate feature importance using multiple methods"""
        
        # Mutual information
        mi_scores = mutual_info_regression(X, y, random_state=self.config.random_state)
        
        # F-statistic
        f_scores, _ = f_regression(X, y)
        
        # Combine scores
        feature_importance = {}
        for i, feature in enumerate(X.columns):
            feature_importance[feature] = {
                'mutual_info': mi_scores[i],
                'f_statistic': f_scores[i],
                'combined': (mi_scores[i] + f_scores[i]) / 2
            }
        
        return feature_importance

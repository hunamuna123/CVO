#!/usr/bin/env python3
"""
Real Estate AI Training Script
Loads dataset and trains price prediction, demand analysis, and recommendation models.
"""

import pandas as pd
import numpy as np
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
import warnings
import torch
warnings.filterwarnings('ignore')

# Visualization imports
from visualization import TrainingVisualizer
# Advanced ensemble import
from models.advanced_ensemble import SuperEnsembleModel

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('training.log')
    ]
)

logger = logging.getLogger(__name__)

def load_and_prepare_data(dataset_path: str, sample_size: int = None) -> pd.DataFrame:
    """Load and prepare the real estate dataset"""
    logger.info(f"Loading dataset from {dataset_path}")
    
    try:
        # Load data
        data = pd.read_csv(dataset_path, delimiter=';')
        logger.info(f"Loaded dataset with shape: {data.shape}")
        logger.info(f"Columns: {list(data.columns)}")
        
        # Sample data if requested (for faster training during development)
        if sample_size and len(data) > sample_size:
            logger.info(f"Sampling {sample_size} rows from {len(data)} total rows")
            data = data.sample(n=sample_size, random_state=42)
        
        # Basic data info
        logger.info(f"Data shape after sampling: {data.shape}")
        logger.info(f"Date range: {data['date'].min()} to {data['date'].max()}")
        logger.info(f"Price range: {data['price'].min():,.0f} to {data['price'].max():,.0f} RUB")
        
        # Handle missing values
        logger.info("Missing values per column:")
        missing_info = data.isnull().sum()
        for col, missing_count in missing_info.items():
            if missing_count > 0:
                logger.info(f"  {col}: {missing_count} ({missing_count/len(data)*100:.1f}%)")
        
        # Basic preprocessing
        # Remove rows with missing essential features
        essential_cols = ['price', 'area', 'rooms']
        data = data.dropna(subset=essential_cols)
        logger.info(f"After removing rows with missing essential data: {data.shape}")
        
        # Filter extreme outliers
        price_q1 = data['price'].quantile(0.01)
        price_q99 = data['price'].quantile(0.99)
        data = data[(data['price'] >= price_q1) & (data['price'] <= price_q99)]
        logger.info(f"After filtering price outliers: {data.shape}")
        
        # Fill missing values for non-essential columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if data[col].isnull().sum() > 0:
                median_val = data[col].median()
                data[col].fillna(median_val, inplace=True)
                logger.info(f"Filled missing values in {col} with median: {median_val}")
        
        return data
        
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        raise


def train_price_prediction_model(data: pd.DataFrame) -> dict:
    """Train price prediction models"""
    logger.info("=== TRAINING PRICE PREDICTION MODEL ===")
    
    try:
        from models.price_prediction import PricePredictionPipeline
        
        # Initialize pipeline
        pipeline = PricePredictionPipeline()
        
        # Prepare data for price prediction (exclude date and id columns)
        feature_cols = [col for col in data.columns if col not in ['date', 'price']]
        price_data = data[feature_cols + ['price']].copy()
        
        logger.info(f"Training with features: {feature_cols}")
        logger.info(f"Price prediction data shape: {price_data.shape}")
        
        # Train ensemble model
        results = pipeline.train(
            data=price_data,
            target_column='price',
            model_type='ensemble',
            optimize_hyperparams=False  # Set to True for optimization (takes longer)
        )
        
        logger.info("Price prediction training completed!")
        logger.info(f"Results: {results}")
        
        # Save model
        model_path = Path("models/saved/price_prediction")
        pipeline.save(model_path)
        logger.info(f"Model saved to {model_path}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error training price prediction model: {e}")
        return {"error": str(e)}


def train_individual_models(data: pd.DataFrame) -> dict:
    """Train individual models for comparison"""
    logger.info("=== TRAINING INDIVIDUAL MODELS ===")
    
    results = {}
    
    try:
        from models.price_prediction import (
            XGBoostPriceModel, 
            LightGBMPriceModel, 
            CatBoostPriceModel,
            PyTorchPriceModel
        )
        from core.data_processing import DataProcessor
        
        # Prepare data
        feature_cols = [col for col in data.columns if col not in ['date', 'price']]
        price_data = data[feature_cols + ['price']].copy()
        
        # Process data
        processor = DataProcessor()
        X_train, X_test, y_train, y_test = processor.prepare_train_test_split(
            price_data, 'price'
        )
        
        # Train individual models
        models = [
            XGBoostPriceModel(),
            LightGBMPriceModel(), 
            CatBoostPriceModel()
        ]
        
        # Add PyTorch if GPU is available
        import torch
        if torch.cuda.is_available():
            logger.info("CUDA available - adding PyTorch model")
            models.append(PyTorchPriceModel())
        else:
            logger.info("CUDA not available - skipping PyTorch model")
        
        for model in models:
            try:
                logger.info(f"Training {model.model_name}...")
                model.fit(X_train, y_train)
                
                # Evaluate
                metrics = model.evaluate(X_test, y_test)
                results[model.model_name] = metrics
                
                logger.info(f"{model.model_name} results: {metrics}")
                
            except Exception as e:
                logger.error(f"Error training {model.model_name}: {e}")
                results[model.model_name] = {"error": str(e)}
        
        return results
        
    except Exception as e:
        logger.error(f"Error training individual models: {e}")
        return {"error": str(e)}


def create_synthetic_demand_data(data: pd.DataFrame) -> pd.DataFrame:
    """Create synthetic demand data for demand analysis training"""
    logger.info("Creating synthetic demand data...")
    
    # Group by date and region to create demand metrics
    demand_data = data.groupby(['date', 'id_region']).agg({
        'price': ['count', 'mean', 'median'],
        'area': 'mean',
        'rooms': 'mean'
    }).reset_index()
    
    # Flatten column names
    demand_data.columns = ['date', 'id_region', 'property_count', 'avg_price', 'median_price', 'avg_area', 'avg_rooms']
    
    # Create demand score (synthetic)
    demand_data['demand_score'] = (
        demand_data['property_count'] * 0.6 + 
        (demand_data['avg_price'] / demand_data['avg_price'].max() * 100) * 0.4
    )
    
    # Add some noise
    np.random.seed(42)
    demand_data['demand_score'] += np.random.normal(0, 5, len(demand_data))
    demand_data['demand_score'] = demand_data['demand_score'].clip(0, 100)
    
    logger.info(f"Created demand data with shape: {demand_data.shape}")
    return demand_data


def train_demand_analysis_model(data: pd.DataFrame) -> dict:
    """Train demand analysis models"""
    logger.info("=== TRAINING DEMAND ANALYSIS MODEL ===")
    
    try:
        from models.demand_analysis import DemandAnalysisPipeline
        
        # Create synthetic demand data
        demand_data = create_synthetic_demand_data(data)
        
        # Initialize pipeline
        pipeline = DemandAnalysisPipeline()
        
        # Sample a region for focused analysis
        sample_region = demand_data['id_region'].value_counts().index[0]
        region_data = demand_data[demand_data['id_region'] == sample_region].copy()
        region_data = region_data.sort_values('date')
        
        logger.info(f"Training demand analysis for region {sample_region}")
        logger.info(f"Demand data shape: {region_data.shape}")
        
        # Rename columns to match expected format
        region_data.rename(columns={'demand_score': 'demand'}, inplace=True)
        
        # Run analysis
        results = pipeline.run_analysis(
            data=region_data,
            property_id=f"region_{sample_region}",
            region=str(sample_region),
            date_column='date',
            target_column='demand'
        )
        
        logger.info("Demand analysis training completed!")
        logger.info(f"Demand metrics: {results.get('demand_metrics', {})}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error training demand analysis model: {e}")
        return {"error": str(e)}


def create_synthetic_interaction_data(data: pd.DataFrame) -> pd.DataFrame:
    """Create synthetic user interaction data for recommendation training"""
    logger.info("Creating synthetic interaction data...")
    
    # Sample properties and create synthetic users
    sample_properties = data.sample(min(1000, len(data)), random_state=42)
    n_users = 100
    
    interactions = []
    
    np.random.seed(42)
    for user_id in range(n_users):
        # Each user interacts with 5-20 properties
        n_interactions = np.random.randint(5, 21)
        user_properties = sample_properties.sample(n_interactions)
        
        for _, prop in user_properties.iterrows():
            # Create interaction based on property characteristics
            interaction_types = ['view', 'view', 'view', 'search', 'contact', 'booking']
            weights = [0.5, 0.3, 0.2, 0.15, 0.08, 0.02]
            
            interaction_type = np.random.choice(interaction_types, p=[w/sum(weights) for w in weights])
            
            interactions.append({
                'user_id': f'user_{user_id}',
                'property_id': f'prop_{prop.name}',
                'interaction_type': interaction_type,
                'timestamp': prop['date']
            })
    
    interaction_data = pd.DataFrame(interactions)
    logger.info(f"Created interaction data with shape: {interaction_data.shape}")
    
    return interaction_data


def train_advanced_ensemble_model(data: pd.DataFrame) -> dict:
    """Train advanced ensemble model for superior performance"""
    logger.info("=== TRAINING ADVANCED ENSEMBLE MODEL ===")
    
    try:
        # Prepare data for advanced ensemble
        feature_cols = [col for col in data.columns if col not in ['date', 'price']]
        ensemble_data = data[feature_cols + ['price']].copy()
        
        logger.info(f"Training advanced ensemble with features: {feature_cols}")
        logger.info(f"Ensemble data shape: {ensemble_data.shape}")
        
        # Initialize advanced ensemble model
        ensemble_model = SuperEnsembleModel(
            use_gpu=torch.cuda.is_available()  # Use GPU if available
        )
        
        # Prepare features and target
        X = ensemble_data.drop('price', axis=1)
        y = ensemble_data['price']
        
        logger.info("Starting advanced ensemble training...")
        logger.info("This may take several minutes due to hyperparameter optimization")
        
        # Train the ensemble model
        ensemble_model.fit(X, y)
        
        # Evaluate the model
        metrics = ensemble_model.evaluate(X, y)
        
        # Get feature importance
        feature_importance = ensemble_model.get_feature_importance()
        
        logger.info("Advanced ensemble training completed!")
        logger.info(f"Ensemble metrics: {metrics}")
        logger.info(f"Top 10 important features: {list(feature_importance.head(10).index)}")
        
        # Save the advanced ensemble model
        ensemble_path = Path("models/saved/advanced_ensemble")
        ensemble_path.mkdir(parents=True, exist_ok=True)
        
        import joblib
        joblib.dump(ensemble_model, ensemble_path / "advanced_ensemble_model.pkl")
        feature_importance.to_csv(ensemble_path / "feature_importance.csv")
        
        logger.info(f"Advanced ensemble model saved to {ensemble_path}")
        
        results = {
            'metrics': metrics,
            'feature_importance': feature_importance.to_dict(),
            'model_path': str(ensemble_path),
            'n_base_models': len(ensemble_model.base_models) if hasattr(ensemble_model, 'base_models') else 'N/A',
            'ensemble_weights': getattr(ensemble_model, 'ensemble_weights', 'N/A')
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Error training advanced ensemble model: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e)}


def train_recommendation_model(data: pd.DataFrame) -> dict:
    """Train recommendation models"""
    logger.info("=== TRAINING RECOMMENDATION MODEL ===")
    
    try:
        from models.recommendation import RecommendationPipeline
        
        # Create synthetic interaction and property data
        interactions = create_synthetic_interaction_data(data)
        
        # Prepare property features
        feature_cols = ['price', 'area', 'kitchen_area', 'rooms', 'level', 'levels', 'building_type', 'object_type']
        properties = data[['price'] + [col for col in feature_cols if col in data.columns]].copy()
        properties.reset_index(inplace=True)
        properties['property_id'] = properties['index'].apply(lambda x: f'prop_{x}')
        properties = properties.drop('index', axis=1)
        
        # Sample for training efficiency
        properties = properties.sample(min(1000, len(properties)), random_state=42)
        
        logger.info(f"Training recommendation system")
        logger.info(f"Interactions shape: {interactions.shape}")
        logger.info(f"Properties shape: {properties.shape}")
        
        # Initialize pipeline
        pipeline = RecommendationPipeline()
        
        # Train model
        results = pipeline.train(
            interactions=interactions,
            properties=properties,
            model_type='collaborative'  # Start with simpler model
        )
        
        logger.info("Recommendation training completed!")
        logger.info(f"Results: {results}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error training recommendation model: {e}")
        return {"error": str(e)}


def main():
    """Main training function"""
    logger.info("=" * 60)
    logger.info("STARTING REAL ESTATE AI MODEL TRAINING")
    logger.info("=" * 60)
    
    # Configuration
    dataset_path = "dataset/input_data.csv"
    sample_size = 5000  # Use subset for faster training, set to None for full dataset
    
    try:
        # Load data
        data = load_and_prepare_data(dataset_path, sample_size)
        
        # Create directories for saving models
        Path("models/saved").mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(parents=True, exist_ok=True)
        
        # Training results
        all_results = {}
        
        # 1. Train advanced ensemble model (primary price prediction)
        logger.info("\n" + "=" * 40)
        advanced_ensemble_results = train_advanced_ensemble_model(data)
        all_results['advanced_ensemble'] = advanced_ensemble_results
        
        # 2. Train price prediction models (original models for comparison)
        logger.info("\n" + "=" * 40)
        price_results = train_price_prediction_model(data)
        all_results['price_prediction'] = price_results
        
        # 3. Train individual models for comparison
        logger.info("\n" + "=" * 40)
        individual_results = train_individual_models(data)
        all_results['individual_models'] = individual_results
        
        # 3. Train demand analysis model
        logger.info("\n" + "=" * 40)
        demand_results = train_demand_analysis_model(data)
        all_results['demand_analysis'] = demand_results
        
        # 4. Train recommendation model
        logger.info("\n" + "=" * 40)
        recommendation_results = train_recommendation_model(data)
        all_results['recommendation'] = recommendation_results
        
        # 5. Generate visualizations
        logger.info("\n" + "=" * 40)
        logger.info("=== GENERATING VISUALIZATIONS ===")
        
        try:
            # Initialize visualizer
            visualizer = TrainingVisualizer(output_dir="visualizations")
            
            # Create data overview plots
            data_overview_path = visualizer.plot_data_overview(data, "Real Estate Dataset Overview")
            logger.info(f"Data overview saved to: {data_overview_path}")
            
            # Create model comparison plots
            if 'individual_models' in all_results and all_results['individual_models']:
                model_comparison_path = visualizer.plot_model_comparison(
                    all_results['individual_models'], 
                    "Price Prediction Model Comparison"
                )
                logger.info(f"Model comparison saved to: {model_comparison_path}")
            
            # Create interactive dashboard
            dashboard_path = visualizer.create_interactive_dashboard(all_results, data)
            logger.info(f"Interactive dashboard saved to: {dashboard_path}")
            
            # Generate comprehensive training report
            report_path = visualizer.create_training_summary_report(all_results, data)
            logger.info(f"Training summary report saved to: {report_path}")
            
            # Save results summary
            summary_path = visualizer.save_results_summary(all_results)
            logger.info(f"Results summary saved to: {summary_path}")
            
            all_results['visualization_paths'] = {
                'data_overview': data_overview_path,
                'model_comparison': model_comparison_path if 'individual_models' in all_results else None,
                'dashboard': dashboard_path,
                'report': report_path,
                'summary': summary_path
            }
            
            logger.info("Visualization generation completed!")
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
            all_results['visualization_error'] = str(e)
        
        # Save results
        results_path = f"training_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        import json
        with open(results_path, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        logger.info("=" * 60)
        logger.info("TRAINING COMPLETED SUCCESSFULLY!")
        logger.info(f"Results saved to: {results_path}")
        logger.info("=" * 60)
        
        # Print summary
        print("\n" + "=" * 60)
        print("TRAINING SUMMARY")
        print("=" * 60)
        
        if 'individual_models' in all_results:
            print("\nIndividual Model Performance:")
            for model_name, metrics in all_results['individual_models'].items():
                if 'error' not in metrics:
                    print(f"  {model_name}:")
                    print(f"    RMSE: {metrics.get('rmse', 'N/A'):,.0f}")
                    print(f"    MAE:  {metrics.get('mae', 'N/A'):,.0f}")
                    print(f"    R²:   {metrics.get('r2', 'N/A'):.3f}")
        
        print(f"\nFull results available in: {results_path}")
        print("Models saved in: models/saved/")
        print("Training logs in: training.log")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

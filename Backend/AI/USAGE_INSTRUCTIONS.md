# Real Estate AI System - Usage Instructions

## 🎉 Training Completed Successfully!

Your Real Estate AI system has been trained and is ready for use. This guide will show you how to use all the trained models and features.

## 📊 Training Results Summary

### Model Performance (RMSE - Lower is Better)
| Model | RMSE | MAE | R² Score | Status |
|-------|------|-----|----------|--------|
| **XGBoost** | 2,687,309 | 1,477,474 | 0.762 | ✅ Best |
| **LightGBM** | 2,916,377 | 1,574,536 | 0.720 | ✅ Good |
| **CatBoost** | 2,859,901 | 1,530,761 | 0.730 | ✅ Good |
| **PyTorch** | 8,038,022 | 5,855,328 | -1.130 | ⚠️ Needs Tuning |

### Dataset Statistics
- **Total Records Processed**: 4,900 properties
- **Features**: 14 property attributes
- **Date Range**: 2021-01-01 to 2021-12-31
- **Price Range**: Various (outliers filtered)

## 🚀 How to Use the AI Models

### 1. Price Prediction

#### Basic Usage
```python
from AI.models.price_prediction import PricePredictionPipeline
import pandas as pd

# Initialize the pipeline
pipeline = PricePredictionPipeline()

# Load the trained model
pipeline.load("models/saved/price_prediction")

# Prepare new property data
new_property = pd.DataFrame({
    'area': [75],
    'kitchen_area': [12],
    'rooms': [3],
    'level': [5],
    'levels': [9],
    'building_type': [4],  # 4=Brick
    'object_type': [0],    # 0=Secondary market
    'geo_lat': [55.7558],
    'geo_lon': [37.6176],
    'postal_code': [125009],
    'street_id': [12345],
    'id_region': [77],     # Moscow region
    'house_id': [67890]
})

# Get price prediction
predicted_price = pipeline.predict(new_property)
print(f"Predicted price: {predicted_price[0]:,.0f} RUB")
```

#### Individual Model Usage
```python
from AI.models.price_prediction import XGBoostPriceModel
from AI.core.data_processing import DataProcessor

# Use best performing model (XGBoost)
model = XGBoostPriceModel()
processor = DataProcessor()

# Load and process your data
# ... data preparation ...

# Train on your data
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)
```

### 2. Recommendation System

#### Generate Property Recommendations
```python
from AI.models.recommendation import RecommendationPipeline
import pandas as pd

# Initialize recommendation system
rec_pipeline = RecommendationPipeline()

# Load trained model (if saved)
# rec_pipeline.load("path/to/recommendation/model")

# Create user interaction data
interactions = pd.DataFrame({
    'user_id': ['user_123'] * 5,
    'property_id': ['prop_1', 'prop_2', 'prop_3', 'prop_4', 'prop_5'],
    'interaction_type': ['view', 'view', 'contact', 'view', 'booking'],
    'timestamp': pd.date_range('2024-01-01', periods=5)
})

# Property features
properties = pd.DataFrame({
    'property_id': ['prop_1', 'prop_2', 'prop_3'],
    'price': [5000000, 7500000, 3500000],
    'area': [65, 85, 45],
    'rooms': [2, 3, 1]
})

# Train recommendation system
rec_pipeline.train(interactions=interactions, properties=properties)

# Get recommendations for a user
recommendations = rec_pipeline.recommend(user_id='user_123', k=10, explain=True)
print("Recommended properties:", recommendations)
```

### 3. Demand Analysis

#### Analyze Market Demand
```python
from AI.models.demand_analysis import DemandAnalysisPipeline
import pandas as pd

# Create demand pipeline
demand_pipeline = DemandAnalysisPipeline()

# Prepare demand data (example with synthetic data)
demand_data = pd.DataFrame({
    'date': pd.date_range('2021-01-01', periods=365),
    'demand': np.random.normal(50, 10, 365),  # Synthetic demand scores
    'property_count': np.random.poisson(20, 365),
    'avg_price': np.random.normal(5000000, 1000000, 365)
})

# Run comprehensive demand analysis
results = demand_pipeline.run_analysis(
    data=demand_data,
    property_id='region_77',  # Moscow
    region='Moscow',
    date_column='date',
    target_column='demand'
)

print("Demand Analysis Results:")
print(f"Current Demand Score: {results['demand_metrics']['current_demand']}")
print(f"Demand Trend: {results['demand_metrics']['trend_30d']}")
print(f"Recommendations: {results['recommendations']}")
```

## 📈 Visualization and Reports

### View Training Results
1. **Interactive Dashboard**: Open `visualizations/interactive_dashboard.html` in your browser
2. **Training Report**: Open `visualizations/training_report.html` for comprehensive results
3. **Data Overview**: View `visualizations/data_overview.png` for dataset insights
4. **Model Comparison**: Check `visualizations/model_comparison.png` for performance comparison

### Generate New Visualizations
```python
from AI.visualization import TrainingVisualizer
import pandas as pd

# Initialize visualizer
viz = TrainingVisualizer(output_dir="my_visualizations")

# Load your data
data = pd.read_csv("your_data.csv")

# Create visualizations
viz.plot_data_overview(data, "My Real Estate Data")
viz.create_interactive_dashboard(results, data)
```

### Live Training Monitoring
```python
from AI.visualization.live_progress import start_live_monitoring

# Start real-time monitoring (during training)
monitor, animation = start_live_monitoring(log_file="training.log")
```

## 🔧 Advanced Configuration

### Model Hyperparameter Tuning
```python
from AI.models.price_prediction import HyperparameterOptimizer, XGBoostPriceModel

# Optimize hyperparameters
optimizer = HyperparameterOptimizer(XGBoostPriceModel, (X_train, y_train))
best_params = optimizer.optimize(n_trials=100)

# Train with optimized parameters
optimized_model = XGBoostPriceModel(**best_params['best_params'])
optimized_model.fit(X_train, y_train)
```

### Custom Data Processing
```python
from AI.core.data_processing import DataProcessor, DataProcessingConfig

# Custom configuration
config = DataProcessingConfig(
    missing_threshold=0.2,
    correlation_threshold=0.9,
    outlier_threshold=0.05
)

# Initialize with custom config
processor = DataProcessor(config)
X_processed = processor.fit_transform(data)
```

## 🗂️ File Structure

```
AI/
├── models/
│   ├── saved/
│   │   └── price_prediction/    # Trained models
│   ├── price_prediction.py
│   ├── demand_analysis.py
│   └── recommendation.py
├── visualizations/
│   ├── training_report.html     # Main report
│   ├── interactive_dashboard.html
│   ├── data_overview.png
│   ├── model_comparison.png
│   └── results_summary.json
├── core/
│   └── data_processing.py
├── config.py
└── training_results_*.json
```

## 📝 Data Format Requirements

### For Price Prediction:
```python
{
    'price': float,           # Price in rubles
    'level': int,            # Apartment floor
    'levels': int,           # Number of storeys
    'rooms': int,            # Number of rooms (-1 for studio)
    'area': float,           # Total area in m²
    'kitchen_area': float,   # Kitchen area in m²
    'geo_lat': float,        # Latitude
    'geo_lon': float,        # Longitude
    'building_type': int,    # 0=Unknown, 1=Other, 2=Panel, 3=Monolithic, 4=Brick, 5=Block, 6=Wood
    'object_type': int,      # 0=Secondary market, 2=New building
    'postal_code': int,      # Postal code
    'street_id': int,        # Street identifier
    'id_region': int,        # Region (85 total in Russia)
    'house_id': int          # House identifier
}
```

### For Demand Analysis:
```python
{
    'date': datetime,        # Date of observation
    'demand': float,         # Demand score (0-100)
    'property_count': int,   # Number of properties
    'avg_price': float,      # Average price in period
    'region': str            # Region identifier
}
```

### For Recommendations:
```python
# User interactions
{
    'user_id': str,          # Unique user identifier
    'property_id': str,      # Property identifier
    'interaction_type': str, # 'view', 'search', 'contact', 'booking'
    'timestamp': datetime    # When interaction occurred
}

# Property features
{
    'property_id': str,      # Unique property identifier
    'price': float,          # Property price
    'area': float,           # Property area
    'rooms': int,            # Number of rooms
    # ... other features
}
```

## 🎯 Best Practices

1. **Data Quality**: Ensure your data follows the required format and has minimal missing values
2. **Feature Engineering**: The system automatically creates additional features, but custom features can improve performance
3. **Model Selection**: XGBoost performed best in training - consider using it for production
4. **Regular Retraining**: Retrain models monthly with new data for best performance
5. **Validation**: Always validate predictions on a holdout test set
6. **Monitoring**: Use the visualization tools to monitor model performance over time

## 🐛 Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure you're in the correct directory and virtual environment
   ```bash
   cd /home/keiske/CVO
   source .venv/bin/activate
   cd AI
   ```

2. **Missing Dependencies**: Install additional packages if needed
   ```bash
   pip install -r requirements.txt
   ```

3. **Data Format Issues**: Ensure your data matches the expected schema
4. **Memory Issues**: Reduce batch size or use data sampling for large datasets
5. **GPU Issues**: PyTorch model requires CUDA; fallback to CPU if needed

### Getting Help:
- Check training logs in `training.log`
- Review error messages in the results JSON files
- Use the visualization tools to understand model behavior
- Refer to the comprehensive training report in `visualizations/training_report.html`

## 🎊 Next Steps

1. **Production Deployment**: Integrate models into your application
2. **API Integration**: Create REST APIs for the models
3. **Continuous Learning**: Set up automated retraining pipelines
4. **A/B Testing**: Compare model performance in production
5. **Feature Enhancement**: Add more data sources and features
6. **Scaling**: Optimize for larger datasets and real-time inference

---

**🎉 Congratulations!** Your Real Estate AI system is ready for production use. The models have been trained successfully and comprehensive visualizations have been generated to help you understand and monitor their performance.

For any questions or issues, refer to the training logs and generated reports for detailed information about the training process and model performance.

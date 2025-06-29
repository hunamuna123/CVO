"""
Training Visualization Module
Comprehensive visualization tools for AI model training processes.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import json

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class TrainingVisualizer:
    """Comprehensive visualization for AI training processes"""
    
    def __init__(self, output_dir: str = "visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Color schemes
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'models': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
        }
    
    def plot_data_overview(self, data: pd.DataFrame, title: str = "Dataset Overview") -> str:
        """Create comprehensive data overview plots"""
        self.logger.info("Creating data overview visualization...")
        
        # Create subplot figure
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # 1. Price distribution
        axes[0, 0].hist(data['price'], bins=50, alpha=0.7, color=self.colors['primary'])
        axes[0, 0].set_title('Price Distribution')
        axes[0, 0].set_xlabel('Price (RUB)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
        
        # 2. Area vs Price scatter
        sample_data = data.sample(min(5000, len(data)))  # Sample for performance
        axes[0, 1].scatter(sample_data['area'], sample_data['price'], 
                          alpha=0.6, color=self.colors['secondary'])
        axes[0, 1].set_title('Area vs Price')
        axes[0, 1].set_xlabel('Area (m²)')
        axes[0, 1].set_ylabel('Price (RUB)')
        axes[0, 1].ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
        
        # 3. Room distribution
        room_counts = data['rooms'].value_counts().sort_index()
        axes[0, 2].bar(room_counts.index, room_counts.values, color=self.colors['success'])
        axes[0, 2].set_title('Room Distribution')
        axes[0, 2].set_xlabel('Number of Rooms')
        axes[0, 2].set_ylabel('Count')
        
        # 4. Building type distribution
        building_counts = data['building_type'].value_counts()
        axes[1, 0].pie(building_counts.values, labels=building_counts.index, autopct='%1.1f%%')
        axes[1, 0].set_title('Building Type Distribution')
        
        # 5. Regional distribution (top 10)
        region_counts = data['id_region'].value_counts().head(10)
        axes[1, 1].bar(range(len(region_counts)), region_counts.values, color=self.colors['info'])
        axes[1, 1].set_title('Top 10 Regions by Property Count')
        axes[1, 1].set_xlabel('Region ID')
        axes[1, 1].set_ylabel('Count')
        axes[1, 1].set_xticks(range(len(region_counts)))
        axes[1, 1].set_xticklabels(region_counts.index, rotation=45)
        
        # 6. Price per square meter
        data_clean = data[(data['area'] > 0) & (data['price'] > 0)]
        price_per_sqm = data_clean['price'] / data_clean['area']
        axes[1, 2].hist(price_per_sqm, bins=50, alpha=0.7, color=self.colors['warning'])
        axes[1, 2].set_title('Price per m² Distribution')
        axes[1, 2].set_xlabel('Price per m² (RUB)')
        axes[1, 2].set_ylabel('Frequency')
        
        plt.tight_layout()
        
        # Save plot
        output_path = self.output_dir / "data_overview.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Data overview saved to {output_path}")
        return str(output_path)
    
    def plot_model_comparison(self, results: Dict[str, Dict], title: str = "Model Performance Comparison") -> str:
        """Create model performance comparison charts"""
        self.logger.info("Creating model comparison visualization...")
        
        # Prepare data
        model_names = []
        rmse_values = []
        mae_values = []
        r2_values = []
        
        for model_name, metrics in results.items():
            if isinstance(metrics, dict) and 'error' not in metrics:
                model_names.append(model_name)
                rmse_values.append(metrics.get('rmse', 0))
                mae_values.append(metrics.get('mae', 0))
                r2_values.append(metrics.get('r2', 0))
        
        if not model_names:
            self.logger.warning("No valid model results to plot")
            return ""
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # 1. RMSE comparison
        bars1 = axes[0, 0].bar(model_names, rmse_values, color=self.colors['models'][:len(model_names)])
        axes[0, 0].set_title('RMSE Comparison (Lower is Better)')
        axes[0, 0].set_ylabel('RMSE')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars1, rmse_values):
            axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                           f'{value:,.0f}', ha='center', va='bottom')
        
        # 2. MAE comparison
        bars2 = axes[0, 1].bar(model_names, mae_values, color=self.colors['models'][:len(model_names)])
        axes[0, 1].set_title('MAE Comparison (Lower is Better)')
        axes[0, 1].set_ylabel('MAE')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars2, mae_values):
            axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                           f'{value:,.0f}', ha='center', va='bottom')
        
        # 3. R² comparison
        bars3 = axes[1, 0].bar(model_names, r2_values, color=self.colors['models'][:len(model_names)])
        axes[1, 0].set_title('R² Score Comparison (Higher is Better)')
        axes[1, 0].set_ylabel('R² Score')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars3, r2_values):
            axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                           f'{value:.3f}', ha='center', va='bottom')
        
        # 4. Combined metrics radar chart
        if len(model_names) > 0:
            # Normalize metrics for radar chart
            rmse_norm = [(max(rmse_values) - x) / (max(rmse_values) - min(rmse_values) + 1e-10) for x in rmse_values]
            mae_norm = [(max(mae_values) - x) / (max(mae_values) - min(mae_values) + 1e-10) for x in mae_values]
            r2_norm = [(x - min(r2_values)) / (max(r2_values) - min(r2_values) + 1e-10) for x in r2_values]
            
            # Create simple performance score
            performance_scores = [np.mean([r, m, r2]) for r, m, r2 in zip(rmse_norm, mae_norm, r2_norm)]
            
            bars4 = axes[1, 1].bar(model_names, performance_scores, color=self.colors['models'][:len(model_names)])
            axes[1, 1].set_title('Overall Performance Score')
            axes[1, 1].set_ylabel('Performance Score (0-1)')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            for bar, value in zip(bars4, performance_scores):
                axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                               f'{value:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Save plot
        output_path = self.output_dir / "model_comparison.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Model comparison saved to {output_path}")
        return str(output_path)
    
    def plot_training_progress(self, training_history: Dict, title: str = "Training Progress") -> str:
        """Plot training progress over epochs"""
        self.logger.info("Creating training progress visualization...")
        
        if not training_history:
            self.logger.warning("No training history to plot")
            return ""
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # Loss curves
        if 'loss' in training_history:
            epochs = range(1, len(training_history['loss']) + 1)
            axes[0].plot(epochs, training_history['loss'], 'b-', label='Training Loss', linewidth=2)
            if 'val_loss' in training_history:
                axes[0].plot(epochs, training_history['val_loss'], 'r-', label='Validation Loss', linewidth=2)
            
            axes[0].set_title('Model Loss')
            axes[0].set_xlabel('Epoch')
            axes[0].set_ylabel('Loss')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
        
        # Metrics curves
        metric_key = None
        for key in ['mae', 'mse', 'accuracy']:
            if key in training_history:
                metric_key = key
                break
        
        if metric_key:
            epochs = range(1, len(training_history[metric_key]) + 1)
            axes[1].plot(epochs, training_history[metric_key], 'g-', 
                        label=f'Training {metric_key.upper()}', linewidth=2)
            
            val_key = f'val_{metric_key}'
            if val_key in training_history:
                axes[1].plot(epochs, training_history[val_key], 'orange', 
                            label=f'Validation {metric_key.upper()}', linewidth=2)
            
            axes[1].set_title(f'Model {metric_key.upper()}')
            axes[1].set_xlabel('Epoch')
            axes[1].set_ylabel(metric_key.upper())
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
        else:
            axes[1].text(0.5, 0.5, 'No metrics available', 
                        ha='center', va='center', transform=axes[1].transAxes)
            axes[1].set_title('Metrics')
        
        plt.tight_layout()
        
        # Save plot
        output_path = self.output_dir / "training_progress.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Training progress saved to {output_path}")
        return str(output_path)
    
    def plot_feature_importance(self, feature_importance: Dict[str, float], 
                              title: str = "Feature Importance", top_n: int = 20) -> str:
        """Plot feature importance"""
        self.logger.info("Creating feature importance visualization...")
        
        if not feature_importance:
            self.logger.warning("No feature importance data to plot")
            return ""
        
        # Sort features by importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        top_features = sorted_features[:top_n]
        
        features, importance = zip(*top_features)
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(range(len(features)), importance, color=self.colors['primary'])
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('Importance Score')
        plt.ylabel('Features')
        plt.yticks(range(len(features)), features)
        plt.gca().invert_yaxis()
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, importance)):
            plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2,
                    f'{value:.3f}', ha='left', va='center')
        
        plt.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        
        # Save plot
        output_path = self.output_dir / "feature_importance.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Feature importance saved to {output_path}")
        return str(output_path)
    
    def create_interactive_dashboard(self, all_results: Dict[str, Any], 
                                   data: pd.DataFrame) -> str:
        """Create an interactive Plotly dashboard"""
        self.logger.info("Creating interactive dashboard...")
        
        # Create subplot figure with multiple charts
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                'Price Distribution', 'Model Performance Comparison',
                'Area vs Price', 'Training Timeline',
                'Regional Analysis', 'Performance Metrics'
            ],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Price distribution
        fig.add_trace(
            go.Histogram(x=data['price'], name='Price Distribution', 
                        marker_color=self.colors['primary']),
            row=1, col=1
        )
        
        # 2. Model performance comparison
        if 'individual_models' in all_results:
            models = all_results['individual_models']
            model_names = []
            rmse_values = []
            
            for name, metrics in models.items():
                if isinstance(metrics, dict) and 'error' not in metrics:
                    model_names.append(name)
                    rmse_values.append(metrics.get('rmse', 0))
            
            if model_names:
                fig.add_trace(
                    go.Bar(x=model_names, y=rmse_values, name='RMSE',
                          marker_color=self.colors['secondary']),
                    row=1, col=2
                )
        
        # 3. Area vs Price scatter
        sample_data = data.sample(min(1000, len(data)))
        fig.add_trace(
            go.Scatter(x=sample_data['area'], y=sample_data['price'],
                      mode='markers', name='Area vs Price',
                      marker=dict(color=self.colors['success'], opacity=0.6)),
            row=2, col=1
        )
        
        # 4. Training timeline (placeholder)
        training_dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        training_progress = np.cumsum(np.random.normal(10, 2, 10))
        
        fig.add_trace(
            go.Scatter(x=training_dates, y=training_progress,
                      mode='lines+markers', name='Training Progress',
                      line=dict(color=self.colors['info'])),
            row=2, col=2
        )
        
        # 5. Regional analysis
        region_counts = data['id_region'].value_counts().head(10)
        fig.add_trace(
            go.Bar(x=region_counts.index.astype(str), y=region_counts.values,
                  name='Properties by Region',
                  marker_color=self.colors['warning']),
            row=3, col=1
        )
        
        # 6. Performance metrics summary
        if 'individual_models' in all_results:
            models = all_results['individual_models']
            metrics_summary = []
            
            for name, metrics in models.items():
                if isinstance(metrics, dict) and 'error' not in metrics:
                    metrics_summary.append({
                        'Model': name,
                        'RMSE': metrics.get('rmse', 0),
                        'MAE': metrics.get('mae', 0),
                        'R²': metrics.get('r2', 0)
                    })
            
            if metrics_summary:
                metrics_df = pd.DataFrame(metrics_summary)
                
                # Create a table-like visualization
                fig.add_trace(
                    go.Bar(x=metrics_df['Model'], y=metrics_df['R²'],
                          name='R² Score', marker_color=self.colors['models'][0]),
                    row=3, col=2
                )
        
        # Update layout
        fig.update_layout(
            height=1000,
            showlegend=True,
            title_text="Real Estate AI Training Dashboard",
            title_x=0.5,
            title_font_size=20
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Price (RUB)", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        
        fig.update_xaxes(title_text="Model", row=1, col=2)
        fig.update_yaxes(title_text="RMSE", row=1, col=2)
        
        fig.update_xaxes(title_text="Area (m²)", row=2, col=1)
        fig.update_yaxes(title_text="Price (RUB)", row=2, col=1)
        
        fig.update_xaxes(title_text="Date", row=2, col=2)
        fig.update_yaxes(title_text="Progress", row=2, col=2)
        
        fig.update_xaxes(title_text="Region ID", row=3, col=1)
        fig.update_yaxes(title_text="Property Count", row=3, col=1)
        
        fig.update_xaxes(title_text="Model", row=3, col=2)
        fig.update_yaxes(title_text="R² Score", row=3, col=2)
        
        # Save interactive dashboard
        output_path = self.output_dir / "interactive_dashboard.html"
        fig.write_html(str(output_path))
        
        self.logger.info(f"Interactive dashboard saved to {output_path}")
        return str(output_path)
    
    def plot_prediction_analysis(self, y_true: np.ndarray, y_pred: np.ndarray, 
                               model_name: str = "Model") -> str:
        """Create prediction analysis plots"""
        self.logger.info(f"Creating prediction analysis for {model_name}...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'{model_name} - Prediction Analysis', fontsize=16, fontweight='bold')
        
        # 1. Actual vs Predicted scatter plot
        max_val = max(np.max(y_true), np.max(y_pred))
        min_val = min(np.min(y_true), np.min(y_pred))
        
        axes[0, 0].scatter(y_true, y_pred, alpha=0.6, color=self.colors['primary'])
        axes[0, 0].plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
        axes[0, 0].set_xlabel('Actual Values')
        axes[0, 0].set_ylabel('Predicted Values')
        axes[0, 0].set_title('Actual vs Predicted')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Residuals plot
        residuals = y_true - y_pred
        axes[0, 1].scatter(y_pred, residuals, alpha=0.6, color=self.colors['secondary'])
        axes[0, 1].axhline(y=0, color='r', linestyle='--')
        axes[0, 1].set_xlabel('Predicted Values')
        axes[0, 1].set_ylabel('Residuals')
        axes[0, 1].set_title('Residuals Plot')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Residuals distribution
        axes[1, 0].hist(residuals, bins=50, alpha=0.7, color=self.colors['success'])
        axes[1, 0].set_xlabel('Residuals')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Residuals Distribution')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Q-Q plot for residuals normality
        from scipy import stats
        stats.probplot(residuals, dist="norm", plot=axes[1, 1])
        axes[1, 1].set_title('Q-Q Plot (Residuals Normality)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        output_path = self.output_dir / f"prediction_analysis_{model_name.lower().replace(' ', '_')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Prediction analysis saved to {output_path}")
        return str(output_path)
    
    def create_training_summary_report(self, all_results: Dict[str, Any], 
                                     data: pd.DataFrame) -> str:
        """Create a comprehensive HTML training summary report"""
        self.logger.info("Creating training summary report...")
        
        # Generate all visualizations
        data_overview_path = self.plot_data_overview(data)
        
        model_comparison_path = ""
        if 'individual_models' in all_results:
            model_comparison_path = self.plot_model_comparison(all_results['individual_models'])
        
        dashboard_path = self.create_interactive_dashboard(all_results, data)
        
        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Real Estate AI Training Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .section {{ margin-bottom: 40px; }}
                .metric-card {{ 
                    display: inline-block; 
                    padding: 20px; 
                    margin: 10px; 
                    border: 1px solid #ddd; 
                    border-radius: 8px; 
                    background-color: #f9f9f9;
                }}
                .chart {{ text-align: center; margin: 20px 0; }}
                img {{ max-width: 100%; height: auto; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Real Estate AI Training Report</h1>
                <p>Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Dataset Overview</h2>
                <div class="metric-card">
                    <h3>Dataset Statistics</h3>
                    <p><strong>Total Records:</strong> {len(data):,}</p>
                    <p><strong>Features:</strong> {len(data.columns)}</p>
                    <p><strong>Date Range:</strong> {data['date'].min()} to {data['date'].max()}</p>
                    <p><strong>Price Range:</strong> {data['price'].min():,.0f} - {data['price'].max():,.0f} RUB</p>
                </div>
                <div class="chart">
                    <img src="{Path(data_overview_path).name}" alt="Data Overview">
                </div>
            </div>
        """
        
        # Add model results
        if 'individual_models' in all_results:
            html_content += """
            <div class="section">
                <h2>Model Performance</h2>
                <table>
                    <tr>
                        <th>Model</th>
                        <th>RMSE</th>
                        <th>MAE</th>
                        <th>R² Score</th>
                        <th>Status</th>
                    </tr>
            """
            
            for model_name, metrics in all_results['individual_models'].items():
                if isinstance(metrics, dict):
                    if 'error' in metrics:
                        html_content += f"""
                        <tr>
                            <td>{model_name}</td>
                            <td colspan="3">Error: {metrics['error']}</td>
                            <td>Failed</td>
                        </tr>
                        """
                    else:
                        html_content += f"""
                        <tr>
                            <td>{model_name}</td>
                            <td>{metrics.get('rmse', 'N/A'):,.0f}</td>
                            <td>{metrics.get('mae', 'N/A'):,.0f}</td>
                            <td>{metrics.get('r2', 'N/A'):.3f}</td>
                            <td>Success</td>
                        </tr>
                        """
            
            html_content += "</table>"
            
            if model_comparison_path:
                html_content += f"""
                <div class="chart">
                    <img src="{Path(model_comparison_path).name}" alt="Model Comparison">
                </div>
                """
            
            html_content += "</div>"
        
        # Add demand analysis results
        if 'demand_analysis' in all_results:
            demand_results = all_results['demand_analysis']
            html_content += f"""
            <div class="section">
                <h2>Demand Analysis Results</h2>
                <div class="metric-card">
                    <h3>Demand Metrics</h3>
            """
            
            if isinstance(demand_results, dict) and 'demand_metrics' in demand_results:
                metrics = demand_results['demand_metrics']
                html_content += f"""
                    <p><strong>Current Demand:</strong> {metrics.get('current_demand', 'N/A'):.2f}</p>
                    <p><strong>Average Demand:</strong> {metrics.get('average_demand', 'N/A'):.2f}</p>
                    <p><strong>Demand Score:</strong> {metrics.get('demand_score', 'N/A'):.2f}</p>
                    <p><strong>Volatility:</strong> {metrics.get('volatility', 'N/A'):.3f}</p>
                """
            
            html_content += "</div></div>"
        
        # Add recommendation system results
        if 'recommendation' in all_results:
            rec_results = all_results['recommendation']
            html_content += f"""
            <div class="section">
                <h2>Recommendation System Results</h2>
                <div class="metric-card">
                    <h3>Training Status</h3>
                    <p><strong>Status:</strong> {rec_results.get('training_status', 'Unknown')}</p>
                    <p><strong>Model Type:</strong> {rec_results.get('model_type', 'Unknown')}</p>
                    <p><strong>Interactions Processed:</strong> {rec_results.get('n_interactions', 'N/A')}</p>
                </div>
            </div>
            """
        
        # Add interactive dashboard link
        html_content += f"""
            <div class="section">
                <h2>Interactive Dashboard</h2>
                <p><a href="{Path(dashboard_path).name}" target="_blank">Open Interactive Dashboard</a></p>
            </div>
            
            <div class="section">
                <h2>Training Configuration</h2>
                <div class="metric-card">
                    <h3>System Information</h3>
                    <p><strong>Python Version:</strong> 3.13</p>
                    <p><strong>Dataset Sample Size:</strong> {len(data):,} records</p>
                    <p><strong>Training Date:</strong> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save HTML report
        report_path = self.output_dir / "training_report.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Training summary report saved to {report_path}")
        return str(report_path)
    
    def save_results_summary(self, all_results: Dict[str, Any]) -> str:
        """Save a JSON summary of all results"""
        summary_path = self.output_dir / "results_summary.json"
        
        with open(summary_path, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        self.logger.info(f"Results summary saved to {summary_path}")
        return str(summary_path)

"""
Live Training Progress Visualization
Real-time monitoring and visualization of model training progress.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import json
import time
from typing import Dict, List, Any
import logging
from pathlib import Path
import threading
import queue

class LiveTrainingMonitor:
    """Real-time training progress monitor with live plots"""
    
    def __init__(self, refresh_interval: int = 2):
        self.refresh_interval = refresh_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Data storage
        self.training_data = {
            'timestamps': [],
            'models_trained': [],
            'current_model': '',
            'current_status': 'Starting...',
            'metrics': {'rmse': [], 'mae': [], 'r2': []},
            'progress_percentage': 0
        }
        
        # Setup matplotlib for real-time plotting
        plt.style.use('seaborn-v0_8')
        self.fig, self.axes = plt.subplots(2, 2, figsize=(15, 10))
        self.fig.suptitle('Real Estate AI Training Progress', fontsize=16, fontweight='bold')
        
        # Colors
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd'
        }
        
        self.setup_plots()
    
    def setup_plots(self):
        """Initialize all plot areas"""
        # 1. Training Progress (top-left)
        self.axes[0, 0].set_title('Training Progress')
        self.axes[0, 0].set_xlabel('Time')
        self.axes[0, 0].set_ylabel('Models Completed')
        self.axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Model Performance (top-right)
        self.axes[0, 1].set_title('Model Performance Comparison')
        self.axes[0, 1].set_xlabel('Model')
        self.axes[0, 1].set_ylabel('RMSE')
        self.axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Training Timeline (bottom-left)
        self.axes[1, 0].set_title('Training Timeline')
        self.axes[1, 0].set_xlabel('Time')
        self.axes[1, 0].set_ylabel('Status')
        self.axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Live Metrics (bottom-right)
        self.axes[1, 1].set_title('Live Metrics')
        self.axes[1, 1].set_xlabel('Training Step')
        self.axes[1, 1].set_ylabel('Metric Value')
        self.axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
    
    def update_progress(self, model_name: str, status: str, metrics: Dict = None, progress: float = 0):
        """Update training progress data"""
        current_time = time.time()
        
        self.training_data['timestamps'].append(current_time)
        self.training_data['current_model'] = model_name
        self.training_data['current_status'] = status
        self.training_data['progress_percentage'] = progress
        
        if status == 'Completed':
            self.training_data['models_trained'].append(model_name)
        
        if metrics:
            for metric, value in metrics.items():
                if metric in self.training_data['metrics']:
                    self.training_data['metrics'][metric].append(value)
        
        self.logger.info(f"Progress updated: {model_name} - {status} ({progress:.1f}%)")
    
    def animate_plots(self, frame):
        """Animation function for live plotting"""
        try:
            # Clear all axes
            for ax in self.axes.flat:
                ax.clear()
            
            self.setup_plots()
            
            # 1. Training Progress
            if self.training_data['timestamps']:
                progress_times = [(t - self.training_data['timestamps'][0]) / 60 for t in self.training_data['timestamps']]
                progress_values = list(range(len(self.training_data['models_trained'])))
                
                if progress_times and progress_values:
                    self.axes[0, 0].plot(progress_times[-len(progress_values):], progress_values, 
                                       'o-', color=self.colors['primary'], linewidth=2, markersize=6)
                
                # Add current progress
                if progress_times:
                    current_progress = len(self.training_data['models_trained'])
                    self.axes[0, 0].axhline(y=current_progress, color=self.colors['warning'], 
                                          linestyle='--', alpha=0.7, label=f'Current: {current_progress} models')
                    self.axes[0, 0].legend()
            
            # 2. Model Performance (placeholder with mock data for demo)
            model_names = ['XGBoost', 'LightGBM', 'CatBoost', 'PyTorch']
            rmse_values = [245000, 238000, 252000, 241000]  # Mock values
            
            bars = self.axes[0, 1].bar(model_names, rmse_values, color=self.colors['secondary'], alpha=0.7)
            self.axes[0, 1].set_title('Model Performance (RMSE)')
            
            # Add value labels
            for bar, value in zip(bars, rmse_values):
                self.axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                                   f'{value:,.0f}', ha='center', va='bottom')
            
            # 3. Training Timeline
            if self.training_data['timestamps']:
                timeline_minutes = [(t - self.training_data['timestamps'][0]) / 60 for t in self.training_data['timestamps']]
                timeline_events = [f"{self.training_data['current_model']}: {self.training_data['current_status']}"]
                
                # Show current status
                if timeline_minutes:
                    self.axes[1, 0].text(0.05, 0.9, f"Current: {self.training_data['current_model']}", 
                                        transform=self.axes[1, 0].transAxes, fontsize=12, fontweight='bold')
                    self.axes[1, 0].text(0.05, 0.8, f"Status: {self.training_data['current_status']}", 
                                        transform=self.axes[1, 0].transAxes, fontsize=10)
                    self.axes[1, 0].text(0.05, 0.7, f"Progress: {self.training_data['progress_percentage']:.1f}%", 
                                        transform=self.axes[1, 0].transAxes, fontsize=10)
                    
                    # Progress bar
                    progress_bar_y = 0.5
                    progress_bar_width = 0.8
                    progress_fill = progress_bar_width * (self.training_data['progress_percentage'] / 100)
                    
                    # Background bar
                    self.axes[1, 0].barh(progress_bar_y, progress_bar_width, height=0.1, 
                                       left=0.05, color='lightgray', transform=self.axes[1, 0].transAxes)
                    # Progress fill
                    self.axes[1, 0].barh(progress_bar_y, progress_fill, height=0.1, 
                                       left=0.05, color=self.colors['success'], transform=self.axes[1, 0].transAxes)
            
            # 4. Live Metrics
            if any(self.training_data['metrics'].values()):
                steps = range(len(self.training_data['metrics']['rmse']))
                
                if self.training_data['metrics']['rmse']:
                    self.axes[1, 1].plot(steps, self.training_data['metrics']['rmse'], 
                                       'o-', color=self.colors['warning'], label='RMSE', linewidth=2)
                
                if self.training_data['metrics']['mae']:
                    self.axes[1, 1].plot(steps, self.training_data['metrics']['mae'], 
                                       's-', color=self.colors['info'], label='MAE', linewidth=2)
                
                if self.training_data['metrics']['r2']:
                    # Scale R² to be visible with other metrics
                    scaled_r2 = [r * 100000 for r in self.training_data['metrics']['r2']]
                    self.axes[1, 1].plot(steps, scaled_r2, 
                                       '^-', color=self.colors['success'], label='R² (×100k)', linewidth=2)
                
                self.axes[1, 1].legend()
            
            plt.tight_layout()
            
        except Exception as e:
            self.logger.error(f"Animation error: {e}")
    
    def start_monitoring(self, log_file: str = "training.log"):
        """Start monitoring training progress from log file"""
        def monitor_logs():
            """Monitor log file for training updates"""
            try:
                log_path = Path(log_file)
                if not log_path.exists():
                    self.logger.warning(f"Log file {log_file} not found")
                    return
                
                last_size = 0
                total_models = 4  # Price prediction, Demand analysis, Recommendation, Individual models
                completed_models = 0
                
                while True:
                    try:
                        current_size = log_path.stat().st_size
                        if current_size > last_size:
                            # Read new content
                            with open(log_path, 'r') as f:
                                f.seek(last_size)
                                new_content = f.read()
                                last_size = current_size
                            
                            # Parse log content for training updates
                            lines = new_content.split('\n')
                            for line in lines:
                                if "TRAINING" in line and "MODEL" in line:
                                    if "PRICE PREDICTION" in line:
                                        self.update_progress("Price Prediction", "Training", progress=(completed_models/total_models)*100)
                                    elif "DEMAND ANALYSIS" in line:
                                        self.update_progress("Demand Analysis", "Training", progress=(completed_models/total_models)*100)
                                    elif "RECOMMENDATION" in line:
                                        self.update_progress("Recommendation", "Training", progress=(completed_models/total_models)*100)
                                    elif "INDIVIDUAL MODELS" in line:
                                        self.update_progress("Individual Models", "Training", progress=(completed_models/total_models)*100)
                                
                                elif "completed" in line.lower() or "training completed" in line.lower():
                                    completed_models += 1
                                    current_model = self.training_data['current_model']
                                    self.update_progress(current_model, "Completed", progress=(completed_models/total_models)*100)
                                
                                elif "Results:" in line and "{" in line:
                                    # Try to parse metrics
                                    try:
                                        result_part = line.split("Results:")[1].strip()
                                        if result_part.startswith('{'):
                                            metrics_data = json.loads(result_part)
                                            if isinstance(metrics_data, dict):
                                                parsed_metrics = {}
                                                for key, value in metrics_data.items():
                                                    if key in ['rmse', 'mae', 'r2'] and isinstance(value, (int, float)):
                                                        parsed_metrics[key] = value
                                                
                                                if parsed_metrics:
                                                    self.update_progress(self.training_data['current_model'], 
                                                                       "Evaluating", parsed_metrics)
                                    except:
                                        pass
                        
                        time.sleep(self.refresh_interval)
                        
                    except Exception as e:
                        self.logger.error(f"Error monitoring logs: {e}")
                        time.sleep(self.refresh_interval)
                        
            except Exception as e:
                self.logger.error(f"Fatal error in log monitoring: {e}")
        
        # Start monitoring in separate thread
        monitor_thread = threading.Thread(target=monitor_logs, daemon=True)
        monitor_thread.start()
        
        # Start animation
        ani = animation.FuncAnimation(self.fig, self.animate_plots, interval=self.refresh_interval*1000, 
                                    blit=False, cache_frame_data=False)
        
        self.logger.info(f"Live monitoring started. Watching {log_file}")
        return ani
    
    def show(self):
        """Display the live monitoring interface"""
        plt.show()
    
    def save_final_report(self, output_path: str = "training_progress_report.png"):
        """Save final training progress report"""
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        self.logger.info(f"Final progress report saved to {output_path}")


def start_live_monitoring(log_file: str = "training.log", refresh_interval: int = 2):
    """Start live training monitoring"""
    monitor = LiveTrainingMonitor(refresh_interval=refresh_interval)
    animation = monitor.start_monitoring(log_file)
    monitor.show()
    return monitor, animation


if __name__ == "__main__":
    # Example usage
    print("Starting live training monitor...")
    print("This will monitor training.log for real-time updates.")
    print("Close the plot window to stop monitoring.")
    
    monitor, ani = start_live_monitoring()

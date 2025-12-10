"""
Visualization utilities for predictions and results
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Optional


def plot_bankroll_over_time(bankroll_history: List[float], save_path: Optional[str] = None):
    """
    Plot bankroll progression over time
    
    Args:
        bankroll_history: List of bankroll values
        save_path: Path to save plot (optional)
    """
    plt.figure(figsize=(12, 6))
    plt.plot(bankroll_history, linewidth=2)
    plt.axhline(y=bankroll_history[0], color='r', linestyle='--', label='Initial Bankroll')
    plt.xlabel('Number of Bets')
    plt.ylabel('Bankroll ($)')
    plt.title('Bankroll Progression Over Time')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_model_performance(metrics_df: pd.DataFrame, save_path: Optional[str] = None):
    """
    Plot model performance comparison
    
    Args:
        metrics_df: DataFrame with model metrics
        save_path: Path to save plot (optional)
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Accuracy comparison
    if 'test_accuracy' in metrics_df.columns:
        axes[0].bar(metrics_df.index, metrics_df['test_accuracy'])
        axes[0].set_ylabel('Accuracy')
        axes[0].set_title('Model Test Accuracy Comparison')
        axes[0].set_ylim([0.5, 0.7])
        axes[0].axhline(y=0.54, color='r', linestyle='--', label='Market Break-even')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
    
    # AUC comparison
    if 'test_auc' in metrics_df.columns:
        axes[1].bar(metrics_df.index, metrics_df['test_auc'])
        axes[1].set_ylabel('AUC')
        axes[1].set_title('Model AUC Comparison')
        axes[1].set_ylim([0.5, 0.8])
        axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_feature_importance(importance_df: pd.DataFrame, top_n: int = 15, 
                            save_path: Optional[str] = None):
    """
    Plot feature importance
    
    Args:
        importance_df: DataFrame with feature importance
        top_n: Number of top features to show
        save_path: Path to save plot (optional)
    """
    plt.figure(figsize=(10, 8))
    
    top_features = importance_df.head(top_n)
    
    plt.barh(range(len(top_features)), top_features['mean'])
    plt.yticks(range(len(top_features)), top_features.index)
    plt.xlabel('Importance')
    plt.title(f'Top {top_n} Most Important Features')
    plt.gca().invert_yaxis()
    plt.grid(True, alpha=0.3, axis='x')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_bet_distribution(bet_history: List[dict], save_path: Optional[str] = None):
    """
    Plot distribution of bet outcomes and sizes
    
    Args:
        bet_history: List of bet records
        save_path: Path to save plot (optional)
    """
    if not bet_history:
        print("No bet history to plot")
        return
    
    df = pd.DataFrame(bet_history)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Win/Loss distribution
    result_counts = df['result'].value_counts()
    axes[0, 0].bar(result_counts.index, result_counts.values)
    axes[0, 0].set_ylabel('Count')
    axes[0, 0].set_title('Bet Outcomes Distribution')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Profit distribution
    axes[0, 1].hist(df['profit'], bins=30, edgecolor='black')
    axes[0, 1].axvline(x=0, color='r', linestyle='--')
    axes[0, 1].set_xlabel('Profit ($)')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Profit Distribution')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Edge distribution
    if 'edge' in df.columns:
        axes[1, 0].hist(df['edge'], bins=30, edgecolor='black')
        axes[1, 0].set_xlabel('Edge')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Betting Edge Distribution')
        axes[1, 0].grid(True, alpha=0.3)
    
    # Cumulative profit
    cumulative_profit = df['profit'].cumsum()
    axes[1, 1].plot(cumulative_profit)
    axes[1, 1].axhline(y=0, color='r', linestyle='--')
    axes[1, 1].set_xlabel('Bet Number')
    axes[1, 1].set_ylabel('Cumulative Profit ($)')
    axes[1, 1].set_title('Cumulative Profit Over Time')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_calibration_curve(y_true: np.ndarray, y_pred_proba: np.ndarray, 
                           n_bins: int = 10, save_path: Optional[str] = None):
    """
    Plot calibration curve to assess probability predictions
    
    Args:
        y_true: True labels
        y_pred_proba: Predicted probabilities
        n_bins: Number of bins for calibration
        save_path: Path to save plot (optional)
    """
    from sklearn.calibration import calibration_curve
    
    prob_true, prob_pred = calibration_curve(y_true, y_pred_proba, n_bins=n_bins)
    
    plt.figure(figsize=(8, 8))
    plt.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration')
    plt.plot(prob_pred, prob_true, 'o-', label='Model')
    plt.xlabel('Predicted Probability')
    plt.ylabel('True Probability')
    plt.title('Calibration Curve')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()

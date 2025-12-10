"""
Machine learning prediction models for basketball games
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, log_loss
from xgboost import XGBClassifier
import joblib
import os
try:
    from ..config import MODEL_TYPES, MODEL_WEIGHTS, TRAIN_TEST_SPLIT, RANDOM_STATE, MODELS_DIR
except ImportError:
    # Fallback for running as script
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import MODEL_TYPES, MODEL_WEIGHTS, TRAIN_TEST_SPLIT, RANDOM_STATE, MODELS_DIR


class BasketballPredictor:
    """Ensemble predictor using multiple ML models"""
    
    def __init__(self):
        self.models = {}
        self.model_weights = MODEL_WEIGHTS
        self.trained = False
        
    def _create_models(self):
        """Initialize all models"""
        models = {
            'logistic_regression': LogisticRegression(
                max_iter=1000,
                random_state=RANDOM_STATE,
                solver='lbfgs'
            ),
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=RANDOM_STATE,
                n_jobs=-1
            ),
            'xgboost': XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=RANDOM_STATE,
                eval_metric='logloss'
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=RANDOM_STATE
            )
        }
        return {k: v for k, v in models.items() if k in MODEL_TYPES}
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, 
              X_test: pd.DataFrame = None, y_test: pd.Series = None) -> dict:
        """
        Train all models
        
        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features (optional)
            y_test: Test target (optional)
            
        Returns:
            Dictionary with training metrics
        """
        self.models = self._create_models()
        results = {}
        
        print("Training models...")
        for name, model in self.models.items():
            print(f"\nTraining {name}...")
            model.fit(X_train, y_train)
            
            # Training performance
            train_pred = model.predict(X_train)
            train_proba = model.predict_proba(X_train)[:, 1]
            train_acc = accuracy_score(y_train, train_pred)
            
            results[name] = {
                'train_accuracy': train_acc,
                'train_auc': roc_auc_score(y_train, train_proba)
            }
            
            # Test performance if provided
            if X_test is not None and y_test is not None:
                test_pred = model.predict(X_test)
                test_proba = model.predict_proba(X_test)[:, 1]
                test_acc = accuracy_score(y_test, test_pred)
                
                results[name].update({
                    'test_accuracy': test_acc,
                    'test_auc': roc_auc_score(y_test, test_proba),
                    'test_log_loss': log_loss(y_test, test_proba)
                })
                
                print(f"  Train Accuracy: {train_acc:.4f}")
                print(f"  Test Accuracy: {test_acc:.4f}")
                print(f"  Test AUC: {results[name]['test_auc']:.4f}")
        
        self.trained = True
        return results
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict probabilities using ensemble of models
        
        Args:
            X: Features to predict
            
        Returns:
            Array of probabilities for home team winning
        """
        if not self.trained:
            raise ValueError("Models must be trained before prediction")
        
        # Get predictions from all models
        predictions = []
        weights = []
        
        for name, model in self.models.items():
            proba = model.predict_proba(X)[:, 1]
            predictions.append(proba)
            weights.append(self.model_weights.get(name, 1.0))
        
        # Weighted average
        predictions = np.array(predictions)
        weights = np.array(weights)
        weights = weights / weights.sum()  # Normalize
        
        ensemble_proba = np.average(predictions, axis=0, weights=weights)
        
        return ensemble_proba
    
    def predict(self, X: pd.DataFrame, threshold: float = 0.5) -> np.ndarray:
        """
        Predict binary outcome
        
        Args:
            X: Features to predict
            threshold: Probability threshold for classification
            
        Returns:
            Array of binary predictions
        """
        proba = self.predict_proba(X)
        return (proba >= threshold).astype(int)
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """
        Evaluate model performance
        
        Args:
            X: Features
            y: True labels
            
        Returns:
            Dictionary with evaluation metrics
        """
        proba = self.predict_proba(X)
        pred = self.predict(X)
        
        metrics = {
            'accuracy': accuracy_score(y, pred),
            'auc': roc_auc_score(y, proba),
            'log_loss': log_loss(y, proba)
        }
        
        return metrics
    
    def get_feature_importance(self, feature_names: list) -> pd.DataFrame:
        """
        Get feature importance from tree-based models
        
        Args:
            feature_names: List of feature names
            
        Returns:
            DataFrame with feature importance
        """
        importance_dict = {}
        
        for name, model in self.models.items():
            if hasattr(model, 'feature_importances_'):
                importance_dict[name] = model.feature_importances_
        
        if not importance_dict:
            return None
        
        importance_df = pd.DataFrame(importance_dict, index=feature_names)
        importance_df['mean'] = importance_df.mean(axis=1)
        importance_df = importance_df.sort_values('mean', ascending=False)
        
        return importance_df
    
    def save_models(self, directory: str = MODELS_DIR) -> None:
        """
        Save trained models to disk
        
        Args:
            directory: Directory to save models
        """
        os.makedirs(directory, exist_ok=True)
        
        for name, model in self.models.items():
            filepath = os.path.join(directory, f"{name}.joblib")
            joblib.dump(model, filepath)
        
        # Save model weights
        weights_path = os.path.join(directory, "model_weights.joblib")
        joblib.dump(self.model_weights, weights_path)
        
        print(f"Models saved to {directory}")
    
    def load_models(self, directory: str = MODELS_DIR) -> None:
        """
        Load trained models from disk
        
        Args:
            directory: Directory containing saved models
        """
        self.models = {}
        
        for model_type in MODEL_TYPES:
            filepath = os.path.join(directory, f"{model_type}.joblib")
            if os.path.exists(filepath):
                self.models[model_type] = joblib.load(filepath)
        
        # Load model weights
        weights_path = os.path.join(directory, "model_weights.joblib")
        if os.path.exists(weights_path):
            self.model_weights = joblib.load(weights_path)
        
        self.trained = len(self.models) > 0
        print(f"Loaded {len(self.models)} models from {directory}")

"""
Maize Drought Resilience Model using Random Forest
"""

import polars as pl
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
import logging

from config.settings import MODEL_PARAMS, BENCHMARK_YIELD

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MaizeResilienceModel:
    """
    Random Forest model for predicting maize drought resilience scores
    """
    
    def __init__(self, model_params=None):
        """Initialize the model with parameters"""
        self.model_params = model_params or MODEL_PARAMS
        self.model = RandomForestRegressor(**self.model_params)
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_trained = False
        
    def prepare_features(self, df):
        """
        Prepare features for the model
        
        Expected columns:
        - Annual_Rainfall_mm: Annual rainfall in millimeters
        - Soil_pH: Soil pH value
        - Soil_Organic_Carbon: Soil organic carbon content
        - Maize_Yield_tonnes_ha: Target variable (yield in tonnes/ha)
        """
        # Select feature columns
        feature_cols = ['Annual_Rainfall_mm', 'Soil_pH', 'Soil_Organic_Carbon']
        target_col = 'Maize_Yield_tonnes_ha'
        
        # Check if required columns exist
        missing_cols = [col for col in feature_cols + [target_col] if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Extract features and target
        X = df.select(feature_cols).to_numpy()
        y = df.select(target_col).to_numpy().ravel()
        
        self.feature_names = feature_cols
        
        return X, y
    
    def train(self, X, y, test_size=0.2, random_state=42):
        """Train the Random Forest model"""
        logger.info("Training maize resilience model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_train_scaled, y_train, cv=5, scoring='r2'
        )
        
        logger.info(f"Model trained successfully!")
        logger.info(f"R² Score: {r2:.4f}")
        logger.info(f"RMSE: {rmse:.4f}")
        logger.info(f"Cross-validation R²: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        self.is_trained = True
        
        return {
            'r2_score': r2,
            'rmse': rmse,
            'cv_r2_mean': cv_scores.mean(),
            'cv_r2_std': cv_scores.std()
        }
    
    def predict_resilience_score(self, rainfall, soil_ph, organic_carbon):
        """
        Predict maize resilience score (0-100%)
        
        Args:
            rainfall: Annual rainfall in mm
            soil_ph: Soil pH value
            organic_carbon: Soil organic carbon content
            
        Returns:
            dict: Contains resilience_score, predicted_yield, and feature_importance
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Prepare input features
        X = np.array([[rainfall, soil_ph, organic_carbon]])
        X_scaled = self.scaler.transform(X)
        
        # Predict yield
        predicted_yield = self.model.predict(X_scaled)[0]
        
        # Calculate resilience score (0-100%)
        resilience_score = min(100, max(0, (predicted_yield / BENCHMARK_YIELD) * 100))
        
        # Get feature importance
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        return {
            'resilience_score': round(resilience_score, 1),
            'predicted_yield': round(predicted_yield, 2),
            'feature_importance': feature_importance,
            'benchmark_yield': BENCHMARK_YIELD
        }
    
    def save_model(self, filepath):
        """Save the trained model and scaler"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load a trained model and scaler"""
        model_data = joblib.load(filepath)
        
        # Handle different model save formats
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        
        # Check if is_trained exists, otherwise infer from model availability
        if 'is_trained' in model_data:
            self.is_trained = model_data['is_trained']
        else:
            # If model exists and has feature_importances_, it's trained
            self.is_trained = (self.model is not None and 
                              hasattr(self.model, 'feature_importances_') and 
                              self.feature_names is not None)
        
        logger.info(f"Model loaded from {filepath}")
        logger.info(f"Model trained status: {self.is_trained}")
        logger.info(f"Feature names: {self.feature_names}")
    
    def get_feature_importance(self):
        """Get feature importance scores"""
        if not self.is_trained:
            raise ValueError("Model must be trained before getting feature importance")
        
        importance_dict = dict(zip(self.feature_names, self.model.feature_importances_))
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))

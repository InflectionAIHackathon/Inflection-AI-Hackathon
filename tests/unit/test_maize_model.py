"""
Unit tests for MaizeResilienceModel
"""

import unittest
import numpy as np
import polars as pl
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.models.maize_resilience_model import MaizeResilienceModel
from config.settings import BENCHMARK_YIELD

class TestMaizeResilienceModel(unittest.TestCase):
    """Test cases for MaizeResilienceModel"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.model = MaizeResilienceModel()
        
        # Create sample data
        self.sample_data = pl.DataFrame({
            'Annual_Rainfall_mm': [800, 1200, 600, 1000],
            'Soil_pH': [6.5, 7.0, 5.5, 6.8],
            'Soil_Organic_Carbon': [2.1, 3.0, 1.5, 2.5],
            'Maize_Yield_tonnes_ha': [4.2, 5.1, 3.8, 4.8]
        })
    
    def test_initialization(self):
        """Test model initialization"""
        self.assertFalse(self.model.is_trained)
        self.assertIsNone(self.model.feature_names)
        self.assertIsNotNone(self.model.model)
        self.assertIsNotNone(self.model.scaler)
    
    def test_prepare_features_valid_data(self):
        """Test feature preparation with valid data"""
        X, y = self.model.prepare_features(self.sample_data)
        
        self.assertEqual(X.shape, (4, 3))
        self.assertEqual(y.shape, (4,))
        self.assertEqual(self.model.feature_names, 
                        ['Annual_Rainfall_mm', 'Soil_pH', 'Soil_Organic_Carbon'])
    
    def test_prepare_features_missing_columns(self):
        """Test feature preparation with missing columns"""
        incomplete_data = self.sample_data.select(['Annual_Rainfall_mm', 'Soil_pH'])
        
        with self.assertRaises(ValueError) as context:
            self.model.prepare_features(incomplete_data)
        
        self.assertIn('Missing required columns', str(context.exception))
    
    def test_model_training(self):
        """Test model training process"""
        X, y = self.model.prepare_features(self.sample_data)
        
        # Mock the RandomForestRegressor to avoid actual training
        with patch.object(self.model.model, 'fit') as mock_fit:
            with patch.object(self.model.model, 'predict') as mock_predict:
                mock_predict.return_value = np.array([4.0, 5.0, 3.5, 4.5])
                
                # Mock cross-validation scores
                with patch('sklearn.model_selection.cross_val_score') as mock_cv:
                    mock_cv.return_value = np.array([0.85, 0.87, 0.83, 0.86, 0.84])
                    
                    results = self.model.train(X, y)
        
        # Verify training results
        self.assertTrue(self.model.is_trained)
        self.assertIn('r2_score', results)
        self.assertIn('rmse', results)
        self.assertIn('cv_r2_mean', results)
    
    def test_predict_resilience_score_not_trained(self):
        """Test prediction without training"""
        with self.assertRaises(ValueError) as context:
            self.model.predict_resilience_score(800, 6.5, 2.1)
        
        self.assertIn('Model must be trained', str(context.exception))
    
    def test_predict_resilience_score_trained(self):
        """Test prediction with trained model"""
        # Train the model first
        X, y = self.model.prepare_features(self.sample_data)
        self.model.train(X, y)
        
        # Mock prediction
        with patch.object(self.model.model, 'predict') as mock_predict:
            mock_predict.return_value = np.array([4.2])
            
            result = self.model.predict_resilience_score(800, 6.5, 2.1)
        
        # Verify prediction results
        self.assertIn('resilience_score', result)
        self.assertIn('predicted_yield', result)
        self.assertIn('feature_importance', result)
        self.assertEqual(result['benchmark_yield'], BENCHMARK_YIELD)
        
        # Test resilience score calculation
        expected_score = (4.2 / BENCHMARK_YIELD) * 100
        self.assertAlmostEqual(result['resilience_score'], expected_score, places=1)
    
    def test_resilience_score_bounds(self):
        """Test resilience score is within 0-100% bounds"""
        X, y = self.model.prepare_features(self.sample_data)
        self.model.train(X, y)
        
        # Test very low yield (should give 0%)
        with patch.object(self.model.model, 'predict') as mock_predict:
            mock_predict.return_value = np.array([0.1])
            result = self.model.predict_resilience_score(100, 4.0, 0.5)
            self.assertEqual(result['resilience_score'], 0.0)
        
        # Test very high yield (should give 100%)
        with patch.object(self.model.model, 'predict') as mock_predict:
            mock_predict.return_value = np.array([10.0])
            result = self.model.predict_resilience_score(2000, 8.0, 5.0)
            self.assertEqual(result['resilience_score'], 100.0)
    
    def test_feature_importance(self):
        """Test feature importance retrieval"""
        X, y = self.model.prepare_features(self.sample_data)
        self.model.train(X, y)
        
        # Mock feature importances
        with patch.object(self.model.model, 'feature_importances_') as mock_importances:
            mock_importances = np.array([0.4, 0.35, 0.25])
            result = self.model.get_feature_importance()
        
        # Verify feature importance structure
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 3)
        self.assertIn('Annual_Rainfall_mm', result)
        self.assertIn('Soil_pH', result)
        self.assertIn('Soil_Organic_Carbon', result)
    
    def test_save_and_load_model(self):
        """Test model saving and loading"""
        import tempfile
        import os
        
        # Train the model
        X, y = self.model.prepare_features(self.sample_data)
        self.model.train(X, y)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Save model
            self.model.save_model(tmp_path)
            self.assertTrue(os.path.exists(tmp_path))
            
            # Create new model instance and load
            new_model = MaizeResilienceModel()
            new_model.load_model(tmp_path)
            
            # Verify loaded model
            self.assertTrue(new_model.is_trained)
            self.assertEqual(new_model.feature_names, self.model.feature_names)
            
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_input_validation(self):
        """Test input validation for prediction"""
        X, y = self.model.prepare_features(self.sample_data)
        self.model.train(X, y)
        
        # Test valid inputs
        try:
            result = self.model.predict_resilience_score(800, 6.5, 2.1)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"Valid inputs should not raise exception: {e}")
        
        # Test invalid rainfall (negative)
        with self.assertRaises(Exception):
            self.model.predict_resilience_score(-100, 6.5, 2.1)
        
        # Test invalid soil pH (out of range)
        with self.assertRaises(Exception):
            self.model.predict_resilience_score(800, 2.0, 2.1)
        
        # Test invalid organic carbon (out of range)
        with self.assertRaises(Exception):
            self.model.predict_resilience_score(800, 6.5, 15.0)

if __name__ == '__main__':
    unittest.main()

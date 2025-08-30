"""
Unit tests for AI Model Development Script
=========================================

This test suite validates the Random Forest model implementation:
- Data preparation and validation
- Model training and evaluation
- Hyperparameter tuning
- Prediction functionality
- Performance metrics calculation
"""

import unittest
import numpy as np
import polars as pl
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import tempfile
import os
import joblib

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from scripts.modeling.ai_model_development import MaizeResilienceModel

class TestMaizeResilienceModel(unittest.TestCase):
    """Test cases for MaizeResilienceModel"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.model = MaizeResilienceModel()
        
        # Create sample data for testing with more realistic sample size
        self.sample_data = pl.DataFrame({
            'County': ['Nakuru', 'Nakuru', 'Baringo', 'Baringo', 'Kisumu', 'Kisumu', 
                      'Machakos', 'Machakos', 'Meru', 'Meru', 'Kakamega', 'Kakamega',
                      'Nyeri', 'Nyeri', 'Embu', 'Embu', 'Tharaka', 'Tharaka', 'Kirinyaga', 'Kirinyaga'],
            'Year': [2020, 2021, 2020, 2021, 2020, 2021, 2020, 2021, 2020, 2021,
                     2020, 2021, 2020, 2021, 2020, 2021, 2020, 2021, 2020, 2021],
            'Monthly_Rainfall_mm': [100, 120, 80, 90, 150, 140, 70, 85, 110, 130,
                                   95, 105, 125, 135, 75, 95, 85, 100, 115, 125],
            'Soil_pH_H2O': [6.5, 6.8, 5.5, 5.8, 7.0, 6.9, 5.2, 5.5, 6.2, 6.5,
                            6.8, 7.1, 6.0, 6.3, 5.8, 6.1, 6.5, 6.8, 6.9, 7.0],
            'Soil_Organic_Carbon': [2.1, 2.3, 1.5, 1.8, 3.0, 2.8, 1.2, 1.5, 2.0, 2.2,
                                   2.5, 2.7, 1.8, 2.0, 1.6, 1.9, 2.1, 2.3, 2.4, 2.6],
            'Maize_Yield_tonnes_ha': [4.2, 4.8, 3.5, 3.8, 5.1, 4.9, 3.2, 3.6, 4.0, 4.3,
                                     4.5, 4.7, 4.1, 4.4, 3.4, 3.7, 3.9, 4.2, 4.6, 4.8]
        })
        
        # Create sample annual data with more realistic sample size
        self.sample_annual_data = pl.DataFrame({
            'Annual_Rainfall_mm': [800, 1200, 600, 1000, 1400, 1300, 500, 700, 1100, 1300,
                                  900, 1100, 1200, 1400, 600, 800, 700, 900, 1000, 1200],
            'Soil_pH': [6.5, 7.0, 5.5, 6.8, 7.0, 6.9, 5.2, 5.5, 6.2, 6.5,
                        6.8, 7.1, 6.0, 6.3, 5.8, 6.1, 6.5, 6.8, 6.9, 7.0],
            'Soil_Organic_Carbon': [2.1, 3.0, 1.5, 2.5, 3.0, 2.8, 1.2, 1.5, 2.0, 2.2,
                                   2.5, 2.7, 1.8, 2.0, 1.6, 1.9, 2.1, 2.3, 2.4, 2.6],
            'Maize_Yield_tonnes_ha': [4.2, 5.1, 3.8, 4.8, 5.1, 4.9, 3.2, 3.6, 4.0, 4.3,
                                     4.5, 4.7, 4.1, 4.4, 3.4, 3.7, 3.9, 4.2, 4.6, 4.8]
        })
    
    def test_initialization(self):
        """Test model initialization"""
        self.assertIsNone(self.model.model)
        self.assertFalse(self.model.is_trained)
        self.assertEqual(self.model.feature_names, ['Annual_Rainfall_mm', 'Soil_pH', 'Soil_Organic_Carbon'])
        self.assertEqual(self.model.target_name, 'Maize_Yield_tonnes_ha')
        self.assertIsNotNone(self.model.scaler)
    
    @patch('polars.read_csv')
    def test_prepare_modeling_data_success(self, mock_read_csv):
        """Test successful data preparation"""
        # Mock the CSV reading
        mock_read_csv.return_value = self.sample_data
        
        # Mock file existence
        with patch('pathlib.Path.exists', return_value=True):
            X, y, annual_data = self.model.prepare_modeling_data()
        
        # Verify output shapes
        self.assertEqual(X.shape, (20, 3))  # 20 samples, 3 features
        self.assertEqual(y.shape, (20,))    # 20 target values
        self.assertEqual(len(annual_data), 20)
        
        # Verify feature names
        self.assertEqual(list(annual_data.columns), 
                        ['County', 'Year', 'Annual_Rainfall_mm', 'Soil_pH', 'Soil_Organic_Carbon', 'Maize_Yield_tonnes_ha'])
    
    @patch('polars.read_csv')
    def test_prepare_modeling_data_missing_file(self, mock_read_csv):
        """Test data preparation with missing file"""
        with patch('pathlib.Path.exists', return_value=False):
            with self.assertRaises(FileNotFoundError):
                self.model.prepare_modeling_data()
    
    @patch('polars.read_csv')
    def test_prepare_modeling_data_no_rainfall_column(self, mock_read_csv):
        """Test data preparation with missing rainfall column"""
        # Create data without rainfall column
        data_no_rainfall = pl.DataFrame({
            'County': ['Nakuru'],
            'Year': [2020],
            'Soil_pH_H2O': [6.5],
            'Soil_Organic_Carbon': [2.1],
            'Maize_Yield_tonnes_ha': [4.2]
        })
        mock_read_csv.return_value = data_no_rainfall
        
        with patch('pathlib.Path.exists', return_value=True):
            with self.assertRaises(ValueError, msg="No rainfall/precipitation column found"):
                self.model.prepare_modeling_data()
    
    @patch('wandb.init')
    @patch('wandb.log')
    def test_train_random_forest_success(self, mock_wandb_log, mock_wandb_init):
        """Test successful Random Forest training"""
        # Mock wandb
        mock_wandb_init.return_value = MagicMock()
        
        # Prepare data
        X = self.sample_annual_data.select(self.model.feature_names).to_numpy()
        y = self.sample_annual_data.select(self.model.target_name).to_numpy().ravel()
        
        # Train model
        results = self.model.train_random_forest(X, y, use_wandb=True)
        
        # Verify model is trained
        self.assertTrue(self.model.is_trained)
        self.assertIsNotNone(self.model.model)
        
        # Verify results structure
        expected_keys = ['train_r2', 'test_r2', 'train_rmse', 'test_rmse', 
                        'cv_r2_mean', 'cv_r2_std', 'feature_importance']
        for key in expected_keys:
            self.assertIn(key, results)
        
        # Verify metrics are numeric
        for key in ['train_r2', 'test_r2', 'train_rmse', 'test_rmse']:
            self.assertIsInstance(results[key], (int, float))
        
        # Verify feature importance
        self.assertIsInstance(results['feature_importance'], dict)
        self.assertEqual(len(results['feature_importance']), 3)
        
        # Verify wandb was called
        mock_wandb_init.assert_called_once()
        mock_wandb_log.assert_called()
    
    @patch('wandb.init')
    def test_train_random_forest_wandb_failure(self, mock_wandb_init):
        """Test training when wandb fails"""
        # Mock wandb failure
        mock_wandb_init.side_effect = Exception("Wandb connection failed")
        
        # Prepare data
        X = self.sample_annual_data.select(self.model.feature_names).to_numpy()
        y = self.sample_annual_data.select(self.model.target_name).to_numpy().ravel()
        
        # Training should continue without wandb
        results = self.model.train_random_forest(X, y, use_wandb=True)
        
        # Verify model is still trained
        self.assertTrue(self.model.is_trained)
        self.assertIsNotNone(self.model.model)
    
    def test_train_random_forest_no_wandb(self):
        """Test training without wandb"""
        # Prepare data
        X = self.sample_annual_data.select(self.model.feature_names).to_numpy()
        y = self.sample_annual_data.select(self.model.target_name).to_numpy().ravel()
        
        # Train model without wandb
        results = self.model.train_random_forest(X, y, use_wandb=False)
        
        # Verify model is trained
        self.assertTrue(self.model.is_trained)
        self.assertIsNotNone(self.model.model)
    
    @patch('wandb.log')
    def test_hyperparameter_tuning_success(self, mock_wandb_log):
        """Test successful hyperparameter tuning"""
        # Prepare data
        X = self.sample_annual_data.select(self.model.feature_names).to_numpy()
        y = self.sample_annual_data.select(self.model.target_name).to_numpy().ravel()
        
        # Perform hyperparameter tuning
        best_model, best_params, best_score = self.model.hyperparameter_tuning(X, y, use_wandb=True)
        
        # Verify output
        self.assertIsNotNone(best_model)
        self.assertIsInstance(best_params, dict)
        self.assertIsInstance(best_score, float)
        
        # Verify best parameters contain expected keys
        expected_param_keys = ['n_estimators', 'max_depth', 'min_samples_split', 'min_samples_leaf']
        for key in expected_param_keys:
            self.assertIn(key, best_params)
        
        # Verify wandb logging
        mock_wandb_log.assert_called()
    
    def test_hyperparameter_tuning_no_wandb(self):
        """Test hyperparameter tuning without wandb"""
        # Prepare data
        X = self.sample_annual_data.select(self.model.feature_names).to_numpy()
        y = self.sample_annual_data.select(self.model.target_name).to_numpy().ravel()
        
        # Perform hyperparameter tuning without wandb
        best_model, best_params, best_score = self.model.hyperparameter_tuning(X, y, use_wandb=False)
        
        # Verify output
        self.assertIsNotNone(best_model)
        self.assertIsInstance(best_params, dict)
        self.assertIsInstance(best_score, float)
    
    def test_predict_resilience_score_not_trained(self):
        """Test prediction without training"""
        with self.assertRaises(ValueError, msg="Model must be trained before making predictions"):
            self.model.predict_resilience_score(800, 6.5, 2.1)
    
    def test_predict_resilience_score_trained(self):
        """Test prediction with trained model"""
        # Train the model first
        X = self.sample_annual_data.select(self.model.feature_names).to_numpy()
        y = self.sample_annual_data.select(self.model.target_name).to_numpy().ravel()
        self.model.train_random_forest(X, y, use_wandb=False)
        
        # Make prediction
        result = self.model.predict_resilience_score(800, 6.5, 2.1)
        
        # Verify result structure
        expected_keys = ['resilience_score', 'predicted_yield', 'feature_importance', 'benchmark_yield']
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Verify data types
        self.assertIsInstance(result['resilience_score'], (int, float))
        self.assertIsInstance(result['predicted_yield'], (int, float))
        self.assertIsInstance(result['feature_importance'], dict)
        self.assertEqual(result['benchmark_yield'], 5.0)
        
        # Verify resilience score bounds
        self.assertGreaterEqual(result['resilience_score'], 0)
        self.assertLessEqual(result['resilience_score'], 100)
    
    def test_resilience_score_calculation(self):
        """Test resilience score calculation logic"""
        # Train the model
        X = self.sample_annual_data.select(self.model.feature_names).to_numpy()
        y = self.sample_annual_data.select(self.model.target_name).to_numpy().ravel()
        self.model.train_random_forest(X, y, use_wandb=False)
        
        # Test very low yield (should give 0%)
        # Mock the predict method to return a very low yield
        original_predict = self.model.model.predict
        self.model.model.predict = MagicMock(return_value=np.array([0.1]))
        
        try:
            result = self.model.predict_resilience_score(100, 4.0, 0.5)
            self.assertEqual(result['resilience_score'], 2.0)  # 0.1/5.0 * 100 = 2.0
        finally:
            # Restore original method
            self.model.model.predict = original_predict
        
        # Test very high yield (should give 100%)
        self.model.model.predict = MagicMock(return_value=np.array([10.0]))
        
        try:
            result = self.model.predict_resilience_score(2000, 8.0, 5.0)
            self.assertEqual(result['resilience_score'], 100.0)  # 10.0/5.0 * 100 = 100.0
        finally:
            # Restore original method
            self.model.model.predict = original_predict
    
    def test_save_model_not_trained(self):
        """Test saving untrained model"""
        # The method logs an error but doesn't raise an exception
        # We should test that it handles the untrained state gracefully
        self.assertFalse(self.model.is_trained)
        
        # Save should not raise an exception, just log an error
        try:
            self.model.save_model()
            # If we get here, no exception was raised (which is correct)
        except Exception as e:
            self.fail(f"save_model() raised an exception when it shouldn't: {e}")
    
    def test_save_model_trained(self):
        """Test saving trained model"""
        # Train the model
        X = self.sample_annual_data.select(self.model.feature_names).to_numpy()
        y = self.sample_annual_data.select(self.model.target_name).to_numpy().ravel()
        self.model.train_random_forest(X, y, use_wandb=False)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Save model
            self.model.save_model(tmp_path)
            self.assertTrue(os.path.exists(tmp_path))
            
            # Verify file size
            file_size = os.path.getsize(tmp_path)
            self.assertGreater(file_size, 0)
            
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_feature_importance_ranking(self):
        """Test feature importance ranking"""
        # Train the model
        X = self.sample_annual_data.select(self.model.feature_names).to_numpy()
        y = self.sample_annual_data.select(self.model.target_name).to_numpy().ravel()
        self.model.train_random_forest(X, y, use_wandb=False)
        
        # Get feature importance
        feature_importance = self.model.model.feature_importances_
        
        # Verify feature importance properties
        self.assertEqual(len(feature_importance), 3)
        self.assertTrue(all(imp >= 0 for imp in feature_importance))
        self.assertAlmostEqual(sum(feature_importance), 1.0, places=5)
    
    def test_model_performance_metrics(self):
        """Test model performance metrics calculation"""
        # Train the model
        X = self.sample_annual_data.select(self.model.feature_names).to_numpy()
        y = self.sample_annual_data.select(self.model.target_name).to_numpy().ravel()
        results = self.model.train_random_forest(X, y, use_wandb=False)
        
        # Verify R² scores are between 0 and 1
        self.assertGreaterEqual(results['train_r2'], 0)
        self.assertLessEqual(results['train_r2'], 1)
        self.assertGreaterEqual(results['test_r2'], 0)
        self.assertLessEqual(results['test_r2'], 1)
        
        # Verify RMSE and MAE are positive
        self.assertGreater(results['train_rmse'], 0)
        self.assertGreater(results['test_rmse'], 0)
        self.assertGreater(results['train_mae'], 0)
        self.assertGreater(results['test_mae'], 0)
        
        # Verify cross-validation scores
        self.assertGreaterEqual(results['cv_r2_mean'], 0)
        self.assertLessEqual(results['cv_r2_mean'], 1)
        self.assertGreaterEqual(results['cv_r2_std'], 0)
    
    def test_data_preprocessing_consistency(self):
        """Test data preprocessing consistency"""
        # Train the model
        X = self.sample_annual_data.select(self.model.feature_names).to_numpy()
        y = self.sample_annual_data.select(self.model.target_name).to_numpy().ravel()
        self.model.train_random_forest(X, y, use_wandb=False)
        
        # Test that scaler transforms data consistently
        X_test = np.array([[800, 6.5, 2.1]])
        X_scaled_1 = self.model.scaler.transform(X_test)
        X_scaled_2 = self.model.scaler.transform(X_test)
        
        # Should be identical
        np.testing.assert_array_equal(X_scaled_1, X_scaled_2)
    
    def test_model_persistence(self):
        """Test model persistence and loading"""
        # Train the model
        X = self.sample_annual_data.select(self.model.feature_names).to_numpy()
        y = self.sample_annual_data.select(self.model.target_name).to_numpy().ravel()
        self.model.train_random_forest(X, y, use_wandb=False)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Save model
            self.model.save_model(tmp_path)
            
            # Load model using joblib
            loaded_data = joblib.load(tmp_path)
            
            # Verify loaded data structure
            self.assertIn('model', loaded_data)
            self.assertIn('scaler', loaded_data)
            self.assertIn('feature_names', loaded_data)
            self.assertIn('target_name', loaded_data)
            self.assertIn('training_date', loaded_data)
            self.assertIn('model_type', loaded_data)
            
            # Verify loaded model can make predictions
            loaded_model = loaded_data['model']
            loaded_scaler = loaded_data['scaler']
            
            X_test = np.array([[800, 6.5, 2.1]])
            X_scaled = loaded_scaler.transform(X_test)
            prediction = loaded_model.predict(X_scaled)
            
            self.assertIsInstance(prediction, np.ndarray)
            self.assertEqual(len(prediction), 1)
            
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

if __name__ == '__main__':
    unittest.main()


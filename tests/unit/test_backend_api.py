"""
Unit tests for the FastAPI backend API
"""

import pytest
import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.api.fastapi_app import app
from src.api.schemas import (
    PredictionRequest, 
    PredictionResponse, 
    PredictionResult,
    ModelInfo,
    BatchPredictionRequest,
    ModelStatus,
    FeatureImportance
)
from src.api.database import (
    PredictionRecord, 
    ModelVersion, 
    TrainingRecord,
    get_db,
    init_database,
    reset_database
)
from src.api.monitoring import MetricsCollector, get_metrics_collector

# Test client
client = TestClient(app)

# Mock data
SAMPLE_PREDICTION_REQUEST = {
    "rainfall": 800.0,
    "soil_ph": 6.5,
    "organic_carbon": 2.1,
    "county": "Nakuru"
}

SAMPLE_PREDICTION_RESULT = {
    "resilience_score": 75.5,
    "yield_prediction": 4.2,
    "confidence_score": 0.85,
    "risk_level": "Low",
    "recommendations": [
        "Maintain current soil management practices",
        "Monitor rainfall patterns",
        "Consider crop rotation"
    ]
}

SAMPLE_MODEL_INFO = {
    "algorithm": "Random Forest",
    "features": ["Annual_Rainfall_mm", "Soil_pH", "Soil_Organic_Carbon"],
    "feature_importance": {
        "Annual_Rainfall_mm": 0.45,
        "Soil_pH": 0.35,
        "Soil_Organic_Carbon": 0.20
    },
    "version": "2.0.0"
}

class TestSchemas:
    """Test Pydantic schemas"""
    
    def test_prediction_request_valid(self):
        """Test valid prediction request"""
        request = PredictionRequest(**SAMPLE_PREDICTION_REQUEST)
        assert request.rainfall == 800.0
        assert request.soil_ph == 6.5
        assert request.organic_carbon == 2.1
        assert request.county == "Nakuru"
    
    def test_prediction_request_invalid_rainfall(self):
        """Test invalid rainfall values"""
        with pytest.raises(ValueError, match="Rainfall must be between 0 and 3000 mm"):
            PredictionRequest(
                rainfall=3500.0,
                soil_ph=6.5,
                organic_carbon=2.1
            )
    
    def test_prediction_request_invalid_soil_ph(self):
        """Test invalid soil pH values"""
        with pytest.raises(ValueError, match="Soil pH must be between 4.0 and 10.0"):
            PredictionRequest(
                rainfall=800.0,
                soil_ph=3.5,
                organic_carbon=2.1
            )
    
    def test_prediction_request_invalid_organic_carbon(self):
        """Test invalid organic carbon values"""
        with pytest.raises(ValueError, match="Organic carbon must be between 0.1 and 10.0%"):
            PredictionRequest(
                rainfall=800.0,
                soil_ph=6.5,
                organic_carbon=0.05
            )
    
    def test_prediction_result_valid(self):
        """Test valid prediction result"""
        result = PredictionResult(**SAMPLE_PREDICTION_RESULT)
        assert result.resilience_score == 75.5
        assert result.yield_prediction == 4.2
        assert result.confidence_score == 0.85
        assert result.risk_level == "Low"
        assert len(result.recommendations) == 3
    
    def test_batch_prediction_request_valid(self):
        """Test valid batch prediction request"""
        batch_request = BatchPredictionRequest(
            predictions=[
                PredictionRequest(**SAMPLE_PREDICTION_REQUEST),
                PredictionRequest(
                    rainfall=900.0,
                    soil_ph=7.0,
                    organic_carbon=2.5,
                    county="Nairobi"
                )
            ]
        )
        assert len(batch_request.predictions) == 2
        assert batch_request.predictions[0].county == "Nakuru"
        assert batch_request.predictions[1].county == "Nairobi"
    
    def test_batch_prediction_request_too_large(self):
        """Test batch prediction request with too many predictions"""
        predictions = [
            PredictionRequest(
                rainfall=800.0 + i,
                soil_ph=6.5,
                organic_carbon=2.1
            ) for i in range(1001)
        ]
        
        with pytest.raises(ValueError, match="Batch size cannot exceed 1000 predictions"):
            BatchPredictionRequest(predictions=predictions)

class TestDatabaseModels:
    """Test database models"""
    
    def test_prediction_record_creation(self):
        """Test creating a prediction record"""
        record = PredictionRecord(
            rainfall=800.0,
            soil_ph=6.5,
            organic_carbon=2.1,
            county="Nakuru",
            resilience_score=75.5,
            yield_prediction=4.2,
            confidence_score=0.85,
            model_version="2.0.0"
        )
        
        assert record.rainfall == 800.0
        assert record.soil_ph == 6.5
        assert record.organic_carbon == 2.1
        assert record.county == "Nakuru"
        assert record.resilience_score == 75.5
        assert record.yield_prediction == 4.2
        assert record.confidence_score == 0.85
        assert record.model_version == "2.0.0"
        assert record.timestamp is not None
    
    def test_model_version_creation(self):
        """Test creating a model version record"""
        record = ModelVersion(
            version="2.0.0",
            training_date=datetime.now(timezone.utc),
            algorithm="Random Forest",
            feature_names='["Annual_Rainfall_mm", "Soil_pH", "Soil_Organic_Carbon"]',
            model_params='{"n_estimators": 100, "max_depth": 10}',
            performance_metrics='{"r2_score": 0.85, "rmse": 0.45}',
            is_active=True
        )
        
        assert record.version == "2.0.0"
        assert record.algorithm == "Random Forest"
        assert record.is_active is True
    
    def test_training_record_creation(self):
        """Test creating a training record"""
        record = TrainingRecord(
            model_version="2.0.0",
            training_start=datetime.now(timezone.utc),
            dataset_size=1000,
            test_size=0.2,
            random_state=42,
            cross_validation_folds=5,
            status="running"
        )
        
        assert record.model_version == "2.0.0"
        assert record.dataset_size == 1000
        assert record.test_size == 0.2
        assert record.status == "running"

class TestMetricsCollector:
    """Test metrics collector"""
    
    def test_metrics_collector_initialization(self):
        """Test metrics collector initialization"""
        collector = MetricsCollector()
        assert collector.prediction_metrics.total_requests == 0
        assert collector.feature_metrics.county_distribution == {}
        assert collector.start_time is not None
    
    def test_record_prediction(self):
        """Test recording prediction metrics"""
        collector = MetricsCollector()
        
        collector.record_prediction(
            rainfall=800.0,
            soil_ph=6.5,
            organic_carbon=2.1,
            resilience_score=75.5,
            processing_time=0.15
        )
        
        assert collector.prediction_metrics.total_requests == 1
        assert collector.prediction_metrics.successful_requests == 1
        assert collector.prediction_metrics.average_processing_time == 0.15
        assert collector.feature_metrics.county_distribution["Unknown"] == 1
    
    def test_record_request(self):
        """Test recording request metrics"""
        collector = MetricsCollector()
        
        collector.record_request(
            endpoint="/api/predict",
            method="POST",
            status_code=200,
            processing_time=0.12
        )
        
        assert collector.endpoint_usage["POST /api/predict"] == 1
        assert len(collector.response_times) == 1
    
    def test_get_metrics(self):
        """Test getting metrics summary"""
        collector = MetricsCollector()
        
        # Add some test data
        collector.record_prediction(
            rainfall=800.0,
            soil_ph=6.5,
            organic_carbon=2.1,
            resilience_score=75.5,
            processing_time=0.15
        )
        
        metrics = collector.get_metrics()
        
        assert metrics["prediction_metrics"]["total_requests"] == 1
        assert metrics["prediction_metrics"]["successful_requests"] == 1
        assert metrics["prediction_metrics"]["failed_requests"] == 0
        assert "timestamp" in metrics
        assert "uptime_seconds" in metrics
    
    def test_reset_metrics(self):
        """Test resetting metrics"""
        collector = MetricsCollector()
        
        # Add some data
        collector.record_prediction(
            rainfall=800.0,
            soil_ph=6.5,
            organic_carbon=2.1,
            resilience_score=75.5
        )
        
        assert collector.prediction_metrics.total_requests == 1
        
        # Reset
        collector.reset_metrics()
        
        assert collector.prediction_metrics.total_requests == 0
        assert len(collector.response_times) == 0

class TestAPIEndpoints:
    """Test API endpoints"""
    
    @patch('src.api.fastapi_app.model')
    def test_root_endpoint(self, mock_model):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Agri-Adapt AI Maize Resilience API"
        assert data["version"] == "2.0.0"
        assert data["status"] == "operational"
    
    @patch('src.api.fastapi_app.model')
    def test_health_check(self, mock_model):
        """Test health check endpoint"""
        mock_model.is_trained = True
        
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data
        assert "components" in data
    
    @patch('src.api.fastapi_app.model')
    def test_get_counties(self, mock_model):
        """Test counties endpoint"""
        response = client.get("/api/counties")
        assert response.status_code == 200
        
        data = response.json()
        assert "counties" in data
        assert "count" in data
        assert len(data["counties"]) > 0
        assert "Nakuru" in data["counties"]
    
    @patch('src.api.fastapi_app.model')
    @patch('src.api.fastapi_app.metrics_collector')
    def test_predict_resilience_success(self, mock_metrics, mock_model):
        """Test successful prediction endpoint"""
        # Mock model
        mock_model.is_trained = True
        mock_model.feature_names = ["Annual_Rainfall_mm", "Soil_pH", "Soil_Organic_Carbon"]
        mock_model.get_feature_importance.return_value = {
            "Annual_Rainfall_mm": 0.45,
            "Soil_pH": 0.35,
            "Soil_Organic_Carbon": 0.20
        }
        mock_model.predict_resilience_score.return_value = SAMPLE_PREDICTION_RESULT
        
        # Mock metrics collector
        mock_metrics.record_prediction.return_value = None
        
        response = client.post("/api/predict", json=SAMPLE_PREDICTION_REQUEST)
        assert response.status_code == 200
        
        data = response.json()
        assert "prediction" in data
        assert "input_parameters" in data
        assert "timestamp" in data
        assert "model_info" in data
        
        # Verify prediction data
        prediction = data["prediction"]
        assert prediction["resilience_score"] == 75.5
        assert prediction["yield_prediction"] == 4.2
        assert prediction["risk_level"] == "Low"
    
    @patch('src.api.fastapi_app.model')
    def test_predict_resilience_model_not_trained(self, mock_model):
        """Test prediction with untrained model"""
        mock_model.is_trained = False
        
        response = client.post("/api/predict", json=SAMPLE_PREDICTION_REQUEST)
        assert response.status_code == 503
        
        data = response.json()
        assert "error" in data
        assert "not trained" in data["error"]
    
    @patch('src.api.fastapi_app.model')
    def test_predict_resilience_invalid_rainfall(self, mock_model):
        """Test prediction with invalid rainfall"""
        mock_model.is_trained = True
        
        invalid_request = SAMPLE_PREDICTION_REQUEST.copy()
        invalid_request["rainfall"] = 3500.0
        
        response = client.post("/api/predict", json=invalid_request)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "Rainfall must be between 0 and 3000 mm" in data["error"]
    
    @patch('src.api.fastapi_app.model')
    def test_predict_resilience_invalid_soil_ph(self, mock_model):
        """Test prediction with invalid soil pH"""
        mock_model.is_trained = True
        
        invalid_request = SAMPLE_PREDICTION_REQUEST.copy()
        invalid_request["soil_ph"] = 3.5
        
        response = client.post("/api/predict", json=invalid_request)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "Soil pH must be between 4.0 and 10.0" in data["error"]
    
    @patch('src.api.fastapi_app.model')
    def test_predict_resilience_invalid_organic_carbon(self, mock_model):
        """Test prediction with invalid organic carbon"""
        mock_model.is_trained = True
        
        invalid_request = SAMPLE_PREDICTION_REQUEST.copy()
        invalid_request["organic_carbon"] = 0.05
        
        response = client.post("/api/predict", json=invalid_request)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "Organic carbon must be between 0.1 and 10.0%" in data["error"]
    
    @patch('src.api.fastapi_app.model')
    def test_model_status(self, mock_model):
        """Test model status endpoint"""
        mock_model.is_trained = True
        mock_model.feature_names = ["Annual_Rainfall_mm", "Soil_pH", "Soil_Organic_Carbon"]
        mock_model.model_params = {"n_estimators": 100, "max_depth": 10}
        
        response = client.get("/api/model/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_trained"] is True
        assert data["algorithm"] == "Random Forest"
        assert "feature_names" in data
        assert "model_params" in data
    
    @patch('src.api.fastapi_app.model')
    def test_feature_importance(self, mock_model):
        """Test feature importance endpoint"""
        mock_model.is_trained = True
        mock_model.get_feature_importance.return_value = {
            "Annual_Rainfall_mm": 0.45,
            "Soil_pH": 0.35,
            "Soil_Organic_Carbon": 0.20
        }
        
        response = client.get("/api/model/feature-importance")
        assert response.status_code == 200
        
        data = response.json()
        assert "feature_importance" in data
        assert "timestamp" in data
        assert data["feature_importance"]["Annual_Rainfall_mm"] == 0.45
    
    @patch('src.api.fastapi_app.model')
    def test_feature_importance_model_not_trained(self, mock_model):
        """Test feature importance with untrained model"""
        mock_model.is_trained = False
        
        response = client.get("/api/model/feature-importance")
        assert response.status_code == 503
        
        data = response.json()
        assert "error" in data
        assert "not trained" in data["error"]

class TestBatchPrediction:
    """Test batch prediction functionality"""
    
    @patch('src.api.fastapi_app.model')
    @patch('src.api.fastapi_app.metrics_collector')
    def test_batch_prediction_success(self, mock_metrics, mock_model):
        """Test successful batch prediction"""
        # Mock model
        mock_model.is_trained = True
        mock_model.feature_names = ["Annual_Rainfall_mm", "Soil_pH", "Soil_Organic_Carbon"]
        mock_model.get_feature_importance.return_value = {
            "Annual_Rainfall_mm": 0.45,
            "Soil_pH": 0.35,
            "Soil_Organic_Carbon": 0.20
        }
        mock_model.predict_resilience_score.return_value = SAMPLE_PREDICTION_RESULT
        
        # Mock metrics collector
        mock_metrics.record_prediction.return_value = None
        
        batch_request = {
            "predictions": [
                SAMPLE_PREDICTION_REQUEST,
                {
                    "rainfall": 900.0,
                    "soil_ph": 7.0,
                    "organic_carbon": 2.5,
                    "county": "Nairobi"
                }
            ]
        }
        
        response = client.post("/api/predict/batch", json=batch_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_processed"] == 2
        assert data["successful_count"] == 2
        assert data["failed_count"] == 0
        assert len(data["results"]) == 2
        
        # Check first result
        first_result = data["results"][0]
        assert first_result["status"] == "success"
        assert first_result["input"]["county"] == "Nakuru"
        assert first_result["prediction"]["resilience_score"] == 75.5
    
    @patch('src.api.fastapi_app.model')
    def test_batch_prediction_with_errors(self, mock_model):
        """Test batch prediction with some errors"""
        mock_model.is_trained = True
        mock_model.predict_resilience_score.side_effect = [
            SAMPLE_PREDICTION_RESULT,  # First prediction succeeds
            ValueError("Invalid parameters")  # Second prediction fails
        ]
        
        batch_request = {
            "predictions": [
                SAMPLE_PREDICTION_REQUEST,
                {
                    "rainfall": 900.0,
                    "soil_ph": 7.0,
                    "organic_carbon": 2.5,
                    "county": "Nairobi"
                }
            ]
        }
        
        response = client.post("/api/predict/batch", json=batch_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_processed"] == 2
        assert data["successful_count"] == 1
        assert data["failed_count"] == 1
        
        # Check results
        successful_results = [r for r in data["results"] if r["status"] == "success"]
        failed_results = [r for r in data["results"] if r["status"] == "error"]
        
        assert len(successful_results) == 1
        assert len(failed_results) == 1
        assert failed_results[0]["error"] == "Invalid parameters"

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_error(self):
        """Test 404 error handling"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert "not found" in data["error"].lower()
    
    @patch('src.api.fastapi_app.model')
    def test_500_error(self, mock_model):
        """Test 500 error handling"""
        mock_model.is_trained = True
        mock_model.predict_resilience_score.side_effect = Exception("Model error")
        
        response = client.post("/api/predict", json=SAMPLE_PREDICTION_REQUEST)
        assert response.status_code == 500
        
        data = response.json()
        assert "error" in data
        assert "Internal server error" in data["error"]

# Performance tests
class TestPerformance:
    """Test API performance"""
    
    @patch('src.api.fastapi_app.model')
    def test_prediction_response_time(self, mock_model):
        """Test prediction endpoint response time"""
        mock_model.is_trained = True
        mock_model.feature_names = ["Annual_Rainfall_mm", "Soil_pH", "Soil_Organic_Carbon"]
        mock_model.get_feature_importance.return_value = {
            "Annual_Rainfall_mm": 0.45,
            "Soil_pH": 0.35,
            "Soil_Organic_Carbon": 0.20
        }
        mock_model.predict_resilience_score.return_value = SAMPLE_PREDICTION_RESULT
        
        import time
        start_time = time.time()
        
        response = client.post("/api/predict", json=SAMPLE_PREDICTION_REQUEST)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
        
        print(f"Prediction response time: {response_time:.4f} seconds")
    
    def test_health_check_response_time(self):
        """Test health check endpoint response time"""
        import time
        start_time = time.time()
        
        response = client.get("/health")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 0.1  # Should respond within 100ms
        
        print(f"Health check response time: {response_time:.4f} seconds")

# Integration tests
class TestIntegration:
    """Test API integration"""
    
    @patch('src.api.fastapi_app.model')
    def test_complete_prediction_flow(self, mock_model):
        """Test complete prediction flow"""
        # Setup mock model
        mock_model.is_trained = True
        mock_model.feature_names = ["Annual_Rainfall_mm", "Soil_pH", "Soil_Organic_Carbon"]
        mock_model.get_feature_importance.return_value = {
            "Annual_Rainfall_mm": 0.45,
            "Soil_pH": 0.35,
            "Soil_Organic_Carbon": 0.20
        }
        mock_model.predict_resilience_score.return_value = SAMPLE_PREDICTION_RESULT
        
        # 1. Check health
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # 2. Get counties
        counties_response = client.get("/api/counties")
        assert counties_response.status_code == 200
        
        # 3. Check model status
        model_status_response = client.get("/api/model/status")
        assert model_status_response.status_code == 200
        
        # 4. Make prediction
        prediction_response = client.post("/api/predict", json=SAMPLE_PREDICTION_REQUEST)
        assert prediction_response.status_code == 200
        
        # 5. Get feature importance
        feature_importance_response = client.get("/api/model/feature-importance")
        assert feature_importance_response.status_code == 200
        
        # Verify all responses contain expected data
        assert "counties" in counties_response.json()
        assert "is_trained" in model_status_response.json()
        assert "prediction" in prediction_response.json()
        assert "feature_importance" in feature_importance_response.json()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])

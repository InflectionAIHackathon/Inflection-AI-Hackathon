"""
Unit tests for Pydantic schemas
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

# Import schemas
from src.api.schemas import (
    PredictionRequest, 
    PredictionResponse, 
    PredictionResult,
    ModelInfo,
    BatchPredictionRequest,
    ModelStatus,
    FeatureImportance
)

# Test data
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

class TestPredictionRequest:
    """Test PredictionRequest schema"""
    
    def test_valid_request(self):
        """Test valid prediction request"""
        request = PredictionRequest(**SAMPLE_PREDICTION_REQUEST)
        assert request.rainfall == 800.0
        assert request.soil_ph == 6.5
        assert request.organic_carbon == 2.1
        assert request.county == "Nakuru"
    
    def test_invalid_rainfall_too_high(self):
        """Test invalid rainfall values (too high)"""
        with pytest.raises(ValidationError):
            PredictionRequest(
                rainfall=3500.0,
                soil_ph=6.5,
                organic_carbon=2.1
            )
    
    def test_invalid_rainfall_negative(self):
        """Test invalid rainfall values (negative)"""
        with pytest.raises(ValidationError):
            PredictionRequest(
                rainfall=-100.0,
                soil_ph=6.5,
                organic_carbon=2.1
            )
    
    def test_invalid_soil_ph_too_low(self):
        """Test invalid soil pH values (too low)"""
        with pytest.raises(ValidationError):
            PredictionRequest(
                rainfall=800.0,
                soil_ph=3.5,
                organic_carbon=2.1
            )
    
    def test_invalid_soil_ph_too_high(self):
        """Test invalid soil pH values (too high)"""
        with pytest.raises(ValidationError):
            PredictionRequest(
                rainfall=800.0,
                soil_ph=10.5,
                organic_carbon=2.1
            )
    
    def test_invalid_organic_carbon_too_low(self):
        """Test invalid organic carbon values (too low)"""
        with pytest.raises(ValidationError):
            PredictionRequest(
                rainfall=800.0,
                soil_ph=6.5,
                organic_carbon=0.05
            )
    
    def test_invalid_organic_carbon_too_high(self):
        """Test invalid organic carbon values (too high)"""
        with pytest.raises(ValidationError):
            PredictionRequest(
                rainfall=800.0,
                soil_ph=6.5,
                organic_carbon=15.0
            )
    
    def test_optional_county(self):
        """Test that county is optional"""
        request = PredictionRequest(
            rainfall=800.0,
            soil_ph=6.5,
            organic_carbon=2.1
        )
        assert request.county is None

class TestPredictionResult:
    """Test PredictionResult schema"""
    
    def test_valid_result(self):
        """Test valid prediction result"""
        result = PredictionResult(**SAMPLE_PREDICTION_RESULT)
        assert result.resilience_score == 75.5
        assert result.yield_prediction == 4.2
        assert result.confidence_score == 0.85
        assert result.risk_level == "Low"
        assert len(result.recommendations) == 3
        assert "Maintain current soil management practices" in result.recommendations
    
    def test_optional_confidence_score(self):
        """Test that confidence score is optional"""
        result_data = SAMPLE_PREDICTION_RESULT.copy()
        del result_data["confidence_score"]
        
        result = PredictionResult(**result_data)
        assert result.confidence_score is None

class TestModelInfo:
    """Test ModelInfo schema"""
    
    def test_valid_model_info(self):
        """Test valid model info"""
        model_info = ModelInfo(**SAMPLE_MODEL_INFO)
        assert model_info.algorithm == "Random Forest"
        assert len(model_info.features) == 3
        assert "Annual_Rainfall_mm" in model_info.features
        assert model_info.feature_importance["Annual_Rainfall_mm"] == 0.45
        assert model_info.version == "2.0.0"

class TestBatchPredictionRequest:
    """Test BatchPredictionRequest schema"""
    
    def test_valid_batch_request(self):
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
    
    def test_batch_request_too_large(self):
        """Test batch prediction request with too many predictions"""
        predictions = [
            PredictionRequest(
                rainfall=800.0 + i,
                soil_ph=6.5,
                organic_carbon=2.1
            ) for i in range(1001)
        ]
        
        with pytest.raises(ValidationError):
            BatchPredictionRequest(predictions=predictions)
    
    def test_batch_request_empty(self):
        """Test batch prediction request with no predictions"""
        with pytest.raises(ValidationError, match="List should have at least 1 item"):
            BatchPredictionRequest(predictions=[])

class TestModelStatus:
    """Test ModelStatus schema"""
    
    def test_valid_model_status(self):
        """Test valid model status"""
        status = ModelStatus(
            is_trained=True,
            algorithm="Random Forest",
            feature_names=["Annual_Rainfall_mm", "Soil_pH"],
            model_params={"n_estimators": 100},
            last_training=None,
            performance_metrics=None
        )
        assert status.is_trained is True
        assert status.algorithm == "Random Forest"
        assert len(status.feature_names) == 2
        assert status.model_params["n_estimators"] == 100

class TestFeatureImportance:
    """Test FeatureImportance schema"""
    
    def test_valid_feature_importance(self):
        """Test valid feature importance"""
        feature_importance = FeatureImportance(
            feature_importance={
                "Annual_Rainfall_mm": 0.45,
                "Soil_pH": 0.35,
                "Soil_Organic_Carbon": 0.20
            },
            timestamp=datetime.now()
        )
        assert len(feature_importance.feature_importance) == 3
        assert feature_importance.feature_importance["Annual_Rainfall_mm"] == 0.45
        assert feature_importance.timestamp is not None

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

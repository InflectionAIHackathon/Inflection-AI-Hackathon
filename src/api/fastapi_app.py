"""
FastAPI application for Agri-Adapt AI Maize Resilience Model
"""

import time
import logging
from contextlib import asynccontextmanager
from pathlib import Path
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
import structlog

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.models.maize_resilience_model import MaizeResilienceModel
from src.api.schemas import (
    PredictionRequest, 
    PredictionResponse, 
    PredictionResult,
    ModelInfo,
    BatchPredictionRequest,
    BatchPredictionResponse,
    BatchPredictionResult,
    ModelStatus,
    FeatureImportance,
    HealthStatus,
    MetricsResponse
)
from src.api.database import get_db, PredictionRecord, ModelVersion
from src.api.monitoring import get_metrics_collector, MetricsCollector
from config.settings import KENYA_COUNTIES

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global variables for model and metrics
model: Optional[MaizeResilienceModel] = None
metrics_collector: Optional[MetricsCollector] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global model, metrics_collector
    
    # Startup
    logger.info("Starting Agri-Adapt AI FastAPI application...")
    
    try:
        # Initialize model
        model = MaizeResilienceModel()
        
        # Try to load existing trained model
        model_path = project_root / "models" / "maize_resilience_rf_model.joblib"
        if model_path.exists():
            model.load_model(str(model_path))
            logger.info("Loaded existing trained model", 
                       model_path=str(model_path),
                       is_trained=model.is_trained)
        else:
            # Try alternative model file
            alt_model_path = project_root / "models" / "maize_resilience_rf_model.pkl"
            if alt_model_path.exists():
                model.load_model(str(alt_model_path))
                logger.info("Loaded existing trained model", 
                           model_path=str(alt_model_path),
                           is_trained=model.is_trained)
            else:
                logger.warning("No existing model found", 
                              model_path=str(model_path),
                              alt_path=str(alt_model_path))
        
        # Initialize metrics collector
        metrics_collector = get_metrics_collector()
        logger.info("Metrics collector initialized")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error("Failed to initialize application", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agri-Adapt AI FastAPI application...")

# Create FastAPI app
app = FastAPI(
    title="Agri-Adapt AI Maize Resilience API",
    description="High-performance API for maize yield prediction and drought resilience assessment",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Agri-Adapt AI Maize Resilience API",
        version="2.0.0",
        description="Comprehensive API for agricultural AI predictions",
        routes=app.routes,
    )
    
    # Custom info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi

# Background tasks
async def store_prediction(
    db,
    rainfall: float,
    soil_ph: float,
    organic_carbon: float,
    county: str,
    resilience_score: float,
    yield_prediction: float,
    processing_time: float
):
    """Store prediction in database"""
    try:
        prediction_record = PredictionRecord(
            rainfall=rainfall,
            soil_ph=soil_ph,
            organic_carbon=organic_carbon,
            county=county or "Unknown",
            resilience_score=resilience_score,
            yield_prediction=yield_prediction,
            processing_time=processing_time,
            model_version="2.0.0"
        )
        db.add(prediction_record)
        db.commit()
        logger.info("Prediction stored in database", prediction_id=prediction_record.id)
    except Exception as e:
        logger.error("Failed to store prediction", error=str(e))
        db.rollback()

async def store_batch_predictions(
    db,
    predictions: List[Dict[str, Any]]
):
    """Store batch predictions in database"""
    try:
        for pred_data in predictions:
            if pred_data.get("status") == "success":
                prediction_record = PredictionRecord(
                    rainfall=pred_data["input"]["rainfall"],
                    soil_ph=pred_data["input"]["soil_ph"],
                    organic_carbon=pred_data["input"]["organic_carbon"],
                    county=pred_data["input"].get("county", "Unknown"),
                    resilience_score=pred_data["prediction"]["resilience_score"],
                    yield_prediction=pred_data["prediction"]["yield_prediction"],
                    processing_time=pred_data.get("processing_time", 0.0),
                    model_version="2.0.0"
                )
                db.add(prediction_record)
        
        db.commit()
        logger.info("Batch predictions stored in database", count=len(predictions))
    except Exception as e:
        logger.error("Failed to store batch predictions", error=str(e))
        db.rollback()

# API Endpoints
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Agri-Adapt AI Maize Resilience API",
        "version": "2.0.0",
        "status": "operational",
        "model_status": "trained" if model and model.is_trained else "not_trained",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "predict": "/api/predict",
            "batch_predict": "/api/predict/batch",
            "model_status": "/api/model/status",
            "feature_importance": "/api/model/feature-importance",
            "metrics": "/api/metrics"
        }
    }

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    try:
        # Check model health
        model_healthy = model is not None and model.is_trained
        
        # Check database health
        from src.api.database import check_database_health
        db_healthy = check_database_health()
        
        # Determine overall status
        if model_healthy and db_healthy:
            status = "healthy"
        elif model_healthy or db_healthy:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return HealthStatus(
            status=status,
            timestamp=datetime.now(timezone.utc),
            service="Agri-Adapt AI API",
            version="2.0.0",
            components={
                "model": "healthy" if model_healthy else "unhealthy",
                "database": "healthy" if db_healthy else "unhealthy",
                "metrics": "healthy"
            }
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return HealthStatus(
            status="unhealthy",
            timestamp=datetime.now(timezone.utc),
            service="Agri-Adapt AI API",
            version="2.0.0",
            components={
                "model": "unknown",
                "database": "unknown",
                "metrics": "unknown"
            }
        )

@app.get("/api/counties")
async def get_counties():
    """Get list of Kenya counties"""
    return {
        "counties": KENYA_COUNTIES,
        "count": len(KENYA_COUNTIES),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_resilience(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    """Predict maize resilience score for given parameters"""
    start_time = time.time()
    
    try:
        # Check if model is trained
        if not model or not model.is_trained:
            raise HTTPException(
                status_code=503,
                detail="Model not trained. Please train the model first."
            )
        
        # Make prediction
        prediction_result = model.predict_resilience_score(
            request.rainfall,
            request.soil_ph,
            request.organic_carbon
        )
        
        # Create response
        response = PredictionResponse(
            prediction=PredictionResult(
                resilience_score=prediction_result["resilience_score"],
                yield_prediction=prediction_result["predicted_yield"],
                confidence_score=0.85,  # Placeholder - implement confidence calculation
                risk_level="Low" if prediction_result["resilience_score"] > 70 else "Medium" if prediction_result["resilience_score"] > 50 else "High",
                recommendations=[
                    "Maintain current soil management practices" if prediction_result["resilience_score"] > 70 else "Consider soil improvement strategies",
                    "Monitor rainfall patterns",
                    "Consider crop rotation",
                    "Optimize irrigation if available"
                ]
            ),
            input_parameters=request,
            timestamp=datetime.now(timezone.utc),
            model_info=ModelInfo(
                algorithm="Random Forest",
                features=model.feature_names,
                feature_importance=prediction_result["feature_importance"],
                version="2.0.0"
            )
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Record metrics
        if metrics_collector:
            metrics_collector.record_prediction(
                rainfall=request.rainfall,
                soil_ph=request.soil_ph,
                organic_carbon=request.organic_carbon,
                resilience_score=prediction_result["resilience_score"],
                processing_time=processing_time,
                success=True
            )
        
        # Store prediction in background
        background_tasks.add_task(
            store_prediction,
            db,
            request.rainfall,
            request.soil_ph,
            request.organic_carbon,
            request.county,
            prediction_result["resilience_score"],
            prediction_result["predicted_yield"],
            processing_time
        )
        
        logger.info("Prediction completed successfully",
                   county=request.county,
                   resilience_score=prediction_result["resilience_score"],
                   processing_time=processing_time)
        
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        # Record error metrics
        if metrics_collector:
            metrics_collector.record_prediction(
                rainfall=request.rainfall,
                soil_ph=request.soil_ph,
                organic_carbon=request.organic_carbon,
                resilience_score=0.0,
                processing_time=processing_time,
                success=False
            )
        
        logger.error("Prediction failed", error=str(e), processing_time=processing_time)
        raise HTTPException(status_code=500, detail="Internal server error during prediction")

@app.post("/api/predict/batch", response_model=BatchPredictionResponse)
async def batch_predict(
    batch_request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    """Process multiple predictions in batch"""
    start_time = time.time()
    results = []
    successful_count = 0
    failed_count = 0
    
    try:
        # Check if model is trained
        if not model or not model.is_trained:
            raise HTTPException(
                status_code=503,
                detail="Model not trained. Please train the model first."
            )
        
        # Process each prediction
        for pred_request in batch_request.predictions:
            try:
                # Make prediction
                prediction_result = model.predict_resilience_score(
                    pred_request.rainfall,
                    pred_request.soil_ph,
                    pred_request.organic_carbon
                )
                
                # Create result
                result = BatchPredictionResult(
                    input=pred_request,
                    prediction=PredictionResult(
                        resilience_score=prediction_result["resilience_score"],
                        yield_prediction=prediction_result["predicted_yield"],
                        confidence_score=0.85,
                        risk_level="Low" if prediction_result["resilience_score"] > 70 else "Medium" if prediction_result["resilience_score"] > 50 else "High",
                        recommendations=[
                            "Maintain current soil management practices" if prediction_result["resilience_score"] > 70 else "Consider soil improvement strategies",
                            "Monitor rainfall patterns",
                            "Consider crop rotation"
                        ]
                    ),
                    status="success"
                )
                
                successful_count += 1
                
            except Exception as e:
                # Handle individual prediction failure
                result = BatchPredictionResult(
                    input=pred_request,
                    prediction=None,
                    status="error",
                    error=str(e)
                )
                failed_count += 1
            
            results.append(result)
        
        # Calculate total processing time
        total_processing_time = time.time() - start_time
        
        # Record metrics
        if metrics_collector:
            for i, result in enumerate(results):
                if result.status == "success":
                    metrics_collector.record_prediction(
                        rainfall=result.input.rainfall,
                        soil_ph=result.input.soil_ph,
                        organic_carbon=result.input.organic_carbon,
                        resilience_score=result.prediction.resilience_score,
                        processing_time=total_processing_time / len(results),
                        success=True
                    )
        
        # Store successful predictions in background
        successful_predictions = [
            {
                "input": {
                    "rainfall": r.input.rainfall,
                    "soil_ph": r.input.soil_ph,
                    "organic_carbon": r.input.organic_carbon,
                    "county": r.input.county
                },
                "prediction": {
                    "resilience_score": r.prediction.resilience_score,
                    "yield_prediction": r.prediction.yield_prediction
                },
                "status": r.status,
                "processing_time": total_processing_time / len(results)
            }
            for r in results if r.status == "success"
        ]
        
        if successful_predictions:
            background_tasks.add_task(store_batch_predictions, db, successful_predictions)
        
        response = BatchPredictionResponse(
            results=results,
            total_processed=len(results),
            successful_count=successful_count,
            failed_count=failed_count,
            timestamp=datetime.now(timezone.utc)
        )
        
        logger.info("Batch prediction completed",
                   total=len(results),
                   successful=successful_count,
                   failed=failed_count,
                   processing_time=total_processing_time)
        
        return response
        
    except Exception as e:
        logger.error("Batch prediction failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error during batch prediction")

@app.get("/api/model/status", response_model=ModelStatus)
async def get_model_status():
    """Get model training status and information"""
    if not model:
        raise HTTPException(status_code=503, detail="Model not initialized")
    
    return ModelStatus(
        is_trained=model.is_trained,
        algorithm="Random Forest",
        feature_names=model.feature_names if model.feature_names else [],
        model_params=model.model_params,
        last_training=None,  # Implement training timestamp tracking
        performance_metrics={
            "r2_score": 0.7,  # Your model's R² score
            "rmse": 0.45,     # Root Mean Square Error
            "cv_score": 0.68  # Cross-validation score
        } if model.is_trained else None
    )

@app.get("/api/model/feature-importance", response_model=FeatureImportance)
async def get_feature_importance():
    """Get feature importance scores"""
    if not model or not model.is_trained:
        raise HTTPException(status_code=503, detail="Model not trained")
    
    try:
        feature_importance = model.get_feature_importance()
        return FeatureImportance(
            feature_importance=feature_importance,
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error("Failed to get feature importance", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve feature importance")

@app.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get application metrics"""
    if not metrics_collector:
        raise HTTPException(status_code=503, detail="Metrics collector not available")
    
    try:
        metrics = metrics_collector.get_metrics()
        
        return MetricsResponse(
            total_predictions=metrics["prediction_metrics"]["total_requests"],
            successful_predictions=metrics["prediction_metrics"]["successful_requests"],
            failed_predictions=metrics["prediction_metrics"]["failed_requests"],
            average_response_time=metrics["prediction_metrics"]["processing_time"]["average_seconds"],
            predictions_per_hour=metrics["prediction_metrics"]["requests_per_hour"],
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    if not metrics_collector:
        return "# Metrics collector not available\n"
    
    try:
        return metrics_collector.get_prometheus_metrics()
    except Exception as e:
        logger.error("Failed to get Prometheus metrics", error=str(e))
        return f"# Error retrieving metrics: {e}\n"

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning("HTTP exception occurred",
                   path=request.url.path,
                   status_code=exc.status_code,
                   detail=exc.detail)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error("Unhandled exception occurred",
                 path=request.url.path,
                 error=str(exc),
                 exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

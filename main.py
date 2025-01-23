import os
import logging
import pickle
from typing import List, Dict, Any

import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, field_validator
from prometheus_client import CollectorRegistry, Gauge, Counter, generate_latest
from fastapi.responses import Response

# Environment-based configuration
PORT = int(os.getenv('PORT', 8000))
MODEL_PATH = os.getenv('MODEL_PATH', 'xgboost_model.sav')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Optimized logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Performance-optimized feature list
FEATURES: List[str] = [
    'total_unsuccessful_calls', 'CustomerServiceInteractionRatio', 
    'MinutesOverUsage', 'TotalRevenueGenerated', 'TotalCallFeaturesUsed', 
    'RetentionCalls', 'RetentionOffersAccepted', 'MadeCallToRetentionTeam', 
    'AdjustmentsToCreditRating', 'MonthlyRevenue', 'TotalRecurringCharge', 
    'OverageMinutes', 'MonthsInService', 'PercChangeMinutes', 'PercChangeRevenues', 
    'HandsetPrice', 'CreditRating', 'IncomeGroup', 'AgeHH1', 'AgeHH2', 'ChildrenInHH'
]

class InputData(BaseModel):
    """Validated input data model."""
    total_unsuccessful_calls: int
    CustomerServiceInteractionRatio: float
    MinutesOverUsage: float
    TotalRevenueGenerated: float
    TotalCallFeaturesUsed: int
    RetentionCalls: int
    RetentionOffersAccepted: int
    MadeCallToRetentionTeam: int
    AdjustmentsToCreditRating: int
    MonthlyRevenue: float
    TotalRecurringCharge: float
    OverageMinutes: float
    MonthsInService: int
    PercChangeMinutes: float
    PercChangeRevenues: float
    HandsetPrice: float
    CreditRating: int
    IncomeGroup: int
    AgeHH1: int
    AgeHH2: int
    ChildrenInHH: int

    @field_validator('*')
    @classmethod
    def check_non_negative(cls, value: Any) -> Any:
        """Validate non-negative numeric inputs."""
        if isinstance(value, (int, float)) and value < 0:
            raise ValueError("Value must not be negative")
        return value

class PredictionResponse(BaseModel):
    """Structured prediction response."""
    predicted_churn: int
    churn_probability: float

class ModelPredictor:
    """Efficient model management and prediction."""
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """Singleton model loading with pickle."""
        try:
            with open(MODEL_PATH, 'rb') as model_file:
                self.model = pickle.load(model_file)
            logger.info(f"Model loaded: {MODEL_PATH}")
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            raise RuntimeError(f"Could not initialize model: {e}")

    def predict(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Optimized prediction method."""
        try:
            df = pd.DataFrame([data])[FEATURES]
            probas = self.model.predict_proba(df)[0]
            return {
                'predicted_churn': int(probas[1] > 0.5),
                'churn_probability': float(probas[1])
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise

def create_app() -> FastAPI:
    """Application factory with Render optimizations."""
    app = FastAPI(
        title="Churn Prediction API", 
        description="Scalable customer churn prediction service"
    )

    # Prometheus metrics
    registry = CollectorRegistry()
    prediction_counter = Counter('churn_predictions_total', 'Total churn predictions', registry=registry)
    prediction_probability = Gauge('churn_probability', 'Churn prediction probability', registry=registry)

    predictor = ModelPredictor()

    @app.post("/predict", response_model=PredictionResponse)
    async def predict_churn(input_data: InputData):
        """Streamlined prediction endpoint with metrics."""
        try:
            result = predictor.predict(input_data.model_dump())
            
            # Update Prometheus metrics
            prediction_counter.inc()
            prediction_probability.set(result['churn_probability'])
            
            return PredictionResponse(**result)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Prediction failed")

    @app.get("/metrics")
    async def get_metrics():
        """Expose Prometheus metrics endpoint."""
        return Response(generate_latest(registry), media_type="text/plain")

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)

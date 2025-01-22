from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, validator, ValidationError
from typing import List
import joblib
import pandas as pd
import numpy as np
import logging
import os
from prometheus_fastapi_instrumentator import Instrumentator

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Churn Prediction API", description="A simple API to predict customer churn.")

# --- Prometheus Instrumentation ---
instrumentator = Instrumentator().instrument(app)
@app.on_event("startup")
async def startup_event():
    instrumentator.expose(app)


# Define the feature set
features = ['total_unsuccessful_calls', 'CustomerServiceInteractionRatio', 'MinutesOverUsage',
            'TotalRevenueGenerated', 'TotalCallFeaturesUsed', 'RetentionCalls',
            'RetentionOffersAccepted', 'MadeCallToRetentionTeam', 'AdjustmentsToCreditRating',
            'MonthlyRevenue', 'TotalRecurringCharge', 'OverageMinutes', 'MonthsInService',
            'PercChangeMinutes', 'PercChangeRevenues', 'HandsetPrice', 'CreditRating',
            'IncomeGroup', 'AgeHH1', 'AgeHH2', 'ChildrenInHH']


# Define the Data Validation Model
class InputData(BaseModel):
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

    # Example validation with Pydantic validators
    @validator('*')
    def check_non_negative(cls, value):
        if isinstance(value, (int, float)) and value < 0:
            raise ValueError("Value must not be negative.")
        return value

class PredictionResponse(BaseModel):
    predicted_churn: int
    churn_probability: float

# --- Model Loading ---
MODEL_PATH = os.getenv("MODEL_PATH", "xgboost_model.sav")  # Load from env var, default path.
pipeline = None  # initialize outside try block
try:
    pipeline = joblib.load(MODEL_PATH)
    logger.info("Model successfully loaded from: %s", MODEL_PATH)
except Exception as e:
    logger.error(f"Error loading model from {MODEL_PATH}: {e}", exc_info=True)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Error loading model: {e}",
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict_churn(input_data: InputData):
    """
    Predict customer churn using a pre-trained model.
    """
    try:
        # Convert input to a Pandas DataFrame
        new_df = pd.DataFrame([input_data.dict()])
        new_df = new_df[features]

        # Make Predictions
        prediction = pipeline.predict(new_df)[0]
        probability = pipeline.predict_proba(new_df)[0][1]

        return PredictionResponse(predicted_churn=int(prediction), churn_probability=float(probability))

    except ValidationError as e:
        logger.error(f"Validation Error: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid Input Data: {e}")

    except Exception as e:
         logger.error(f"Error during prediction: {e}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during prediction: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
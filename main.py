from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
import pickle
import pandas as pd
import logging
import os

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Churn Prediction API", description="Predict customer churn.")

# Define the feature set
features = [
    'total_unsuccessful_calls', 'CustomerServiceInteractionRatio', 'MinutesOverUsage',
    'TotalRevenueGenerated', 'TotalCallFeaturesUsed', 'RetentionCalls',
    'RetentionOffersAccepted', 'MadeCallToRetentionTeam', 'AdjustmentsToCreditRating',
    'MonthlyRevenue', 'TotalRecurringCharge', 'OverageMinutes', 'MonthsInService',
    'PercChangeMinutes', 'PercChangeRevenues', 'HandsetPrice', 'CreditRating',
    'IncomeGroup', 'AgeHH1', 'AgeHH2', 'ChildrenInHH'
]

# Input data model
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

class PredictionResponse(BaseModel):
    predicted_churn: int
    churn_probability: float

# Load the model
MODEL_PATH = os.getenv("MODEL_PATH", "xgboost_model.sav")
try:
    with open(MODEL_PATH, 'rb') as file:
        model = pickle.load(file)
    logger.info("Model successfully loaded from %s", MODEL_PATH)
except Exception as e:
    logger.error("Failed to load the model: %s", e)
    raise RuntimeError(f"Error loading model: {e}")

@app.post("/predict", response_model=PredictionResponse)
async def predict_churn(input_data: InputData):
    """
    Predict customer churn using the pre-trained model.
    """
    try:
        # Convert input to a Pandas DataFrame
        data_df = pd.DataFrame([input_data.dict()])[features]

        # Make predictions
        predicted_churn = model.predict(data_df)[0]
        churn_probability = model.predict_proba(data_df)[0][1]

        return PredictionResponse(
            predicted_churn=int(predicted_churn),
            churn_probability=float(churn_probability)
        )
    except Exception as e:
        logger.error("Prediction error: %s", e)
        raise HTTPException(status_code=500, detail="Error during prediction.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

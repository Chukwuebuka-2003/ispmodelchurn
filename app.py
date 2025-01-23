from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError
from flask_cors import CORS  # Import Flask-CORS
import pickle
import pandas as pd
import logging
import os

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/predict": {"origins": ["http://localhost:5173", "https://your-frontend-url.com"]}})  # Adjust as needed

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

# Load the model
MODEL_PATH = os.getenv("MODEL_PATH", "lr_model.sav")
try:
    with open(MODEL_PATH, 'rb') as file:
        model = pickle.load(file)
    logger.info("Model successfully loaded from %s", MODEL_PATH)
except Exception as e:
    logger.error("Failed to load the model: %s", e)
    raise RuntimeError(f"Error loading model: {e}")

@app.route('/predict', methods=['POST'])
def predict_churn():
    """
    Predict customer churn using the pre-trained model.
    """
    try:
        # Parse and validate input data
        input_json = request.json
        input_data = InputData(**input_json)

        # Convert input to a Pandas DataFrame
        data_df = pd.DataFrame([input_data.dict()])[features]

        # Make predictions
        predicted_churn = model.predict(data_df)[0]
        churn_probability = model.predict_proba(data_df)[0][1]

        return jsonify({
            'predicted_churn': int(predicted_churn),
            'churn_probability': float(churn_probability)
        })

    except ValidationError as e:
        logger.error("Validation error: %s", e)
        return jsonify({'error': 'Invalid input data', 'details': e.errors()}), 400

    except Exception as e:
        logger.error("Prediction error: %s", e)
        return jsonify({'error': 'Error during prediction', 'details': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

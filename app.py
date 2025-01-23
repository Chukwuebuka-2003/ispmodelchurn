from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError, validator
from flask_cors import CORS  # Import Flask-CORS
import pickle
import pandas as pd
import logging
import os
from sklearn.preprocessing import MinMaxScaler

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/predict": {"origins": os.getenv('CORS_ORIGINS', ["https://ispmodelchurn.vercel.app"]) }})  # Adjust as needed


# Define the feature set
numerical_features = ['total_unsuccessful_calls', 'CustomerServiceInteractionRatio', 'MinutesOverUsage',
                     'TotalRevenueGenerated', 'TotalCallFeaturesUsed', 'MonthlyRevenue', 'TotalRecurringCharge',
                     'OverageMinutes', 'MonthsInService', 'PercChangeMinutes', 'PercChangeRevenues',
                     'HandsetPrice']
label_encoded_features = ['CreditRating', 'IncomeGroup', 'AgeHH1', 'AgeHH2', 'ChildrenInHH']
binary_features = ['RetentionCalls', 'RetentionOffersAccepted', 'MadeCallToRetentionTeam', 'AdjustmentsToCreditRating']
features = numerical_features + label_encoded_features + binary_features

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

    @validator('*', pre=True)
    def check_field_exists(cls, value, field):
      if value is None:
        raise ValueError(f"{field.name} was not provided")
      return value


# Load the model and the scaler
MODEL_PATH = os.getenv("MODEL_PATH", "xgboost_model.sav")
SCALER_PATH = os.getenv("SCALER_PATH", "minmax_scaler.sav")
try:
    with open(MODEL_PATH, 'rb') as file:
        model = pickle.load(file)
    logger.info("Model successfully loaded from %s", MODEL_PATH)
except Exception as e:
    logger.error("Failed to load the model: %s", e)
    raise RuntimeError(f"Error loading model: {e}")

try:
    with open(SCALER_PATH, 'rb') as file:
        scaler = pickle.load(file)
    logger.info("Scaler successfully loaded from %s", SCALER_PATH)
except Exception as e:
    logger.error("Failed to load the scaler: %s", e)
    raise RuntimeError(f"Error loading scaler: {e}")

@app.route('/predict', methods=['POST'])
def predict_churn():
    """
    Predict customer churn using the pre-trained model.
    """
    try:
        # Parse and validate input data
        input_json = request.get_json()
        InputData(**input_json)
        
        # Convert input to a Pandas DataFrame
        data_df = pd.DataFrame(input_json, index = [0])

        # Create separate dataframes for numerical, label encoded, and binary features
        input_data_numerical = data_df[numerical_features + label_encoded_features]
        input_data_binary = data_df[binary_features]

        # Scale numerical and label encoded features
        scaled_data = scaler.transform(input_data_numerical)
        scaled_df = pd.DataFrame(scaled_data, columns = numerical_features + label_encoded_features, index = data_df.index)

        # Combine the features
        preprocessed_input = pd.concat([scaled_df.reset_index(drop = True), input_data_binary.reset_index(drop = True)], axis=1)

        # Make predictions
        predicted_churn = model.predict(preprocessed_input)[0]
        churn_probability = model.predict_proba(preprocessed_input)[0][1]

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

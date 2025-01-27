from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pickle
import pandas as pd
import logging
import os
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///predictions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model with explicit probability storage
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Input features
    total_unsuccessful_calls = db.Column(db.Integer)
    CustomerServiceInteractionRatio = db.Column(db.Float)
    MinutesOverUsage = db.Column(db.Float)
    TotalRevenueGenerated = db.Column(db.Float)
    TotalCallFeaturesUsed = db.Column(db.Integer)
    RetentionCalls = db.Column(db.Integer)
    RetentionOffersAccepted = db.Column(db.Integer)
    MadeCallToRetentionTeam = db.Column(db.Integer)
    AdjustmentsToCreditRating = db.Column(db.Integer)
    MonthlyRevenue = db.Column(db.Float)
    TotalRecurringCharge = db.Column(db.Float)
    OverageMinutes = db.Column(db.Float)
    MonthsInService = db.Column(db.Integer)
    PercChangeMinutes = db.Column(db.Float)
    PercChangeRevenues = db.Column(db.Float)
    HandsetPrice = db.Column(db.Float)
    CreditRating = db.Column(db.Integer)
    IncomeGroup = db.Column(db.Integer)
    AgeHH1 = db.Column(db.Integer)
    AgeHH2 = db.Column(db.Integer)
    ChildrenInHH = db.Column(db.Integer)
    
    # Prediction outputs
    predicted_churn = db.Column(db.Integer)     # Binary prediction (0 or 1)
    churn_probability = db.Column(db.Float)     # Probability score (0.0-1.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

# CORS configuration
CORS(app, resources={r"/*": {
    "origins": ["http://localhost:5173", "https://ispmodelchurn.vercel.app"],
    "methods": ["GET", "POST"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# Feature configuration
numerical_features = [
    'total_unsuccessful_calls', 'CustomerServiceInteractionRatio', 'MinutesOverUsage',
    'TotalRevenueGenerated', 'TotalCallFeaturesUsed', 'MonthlyRevenue', 'TotalRecurringCharge',
    'OverageMinutes', 'MonthsInService', 'PercChangeMinutes', 'PercChangeRevenues', 'HandsetPrice'
]
label_encoded_features = ['CreditRating', 'IncomeGroup', 'AgeHH1', 'AgeHH2', 'ChildrenInHH']
binary_features = [
    'RetentionCalls', 'RetentionOffersAccepted', 
    'MadeCallToRetentionTeam', 'AdjustmentsToCreditRating'
]

# Input validation model
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

# Load model and scaler
MODEL_PATH = os.getenv("MODEL_PATH", "lr_model.sav")
SCALER_PATH = os.getenv("SCALER_PATH", "minmax_scaler.sav")

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error("Model loading failed: %s", e)
    raise RuntimeError("Model loading failed")

try:
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
    logger.info("Scaler loaded successfully")
except Exception as e:
    logger.error("Scaler loading failed: %s", e)
    raise RuntimeError("Scaler loading failed")

@app.route('/predict', methods=['POST'])
def predict_churn():
    try:
        # Validate and parse input
        input_data = InputData(**request.get_json()).dict()
        data_df = pd.DataFrame(input_data, index=[0])

        # Preprocess data
        numerical_data = data_df[numerical_features + label_encoded_features]
        binary_data = data_df[binary_features]
        
        scaled_numerical = scaler.transform(numerical_data)
        scaled_df = pd.DataFrame(
            scaled_numerical, 
            columns=numerical_features + label_encoded_features,
            index=data_df.index
        )
        
        processed_input = pd.concat(
            [scaled_df.reset_index(drop=True), binary_data.reset_index(drop=True)], 
            axis=1
        )

        # Generate predictions
        prediction = model.predict(processed_input)[0]
        probability = model.predict_proba(processed_input)[0][1]  # Get probability

        # Store full record with probability
        db.session.add(Prediction(
            **input_data,
            predicted_churn=int(prediction),
            churn_probability=float(probability)  # Explicit probability storage
        ))
        db.session.commit()

        return jsonify({
            'predicted_churn': int(prediction),
            'churn_probability': float(probability)
        })

    except ValidationError as e:
        logger.error("Validation error: %s", e)
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        logger.error("Prediction failed: %s", e)
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/model_predictions', methods=['GET'])
def get_predictions():
    try:
        predictions = Prediction.query.order_by(Prediction.timestamp.desc()).all()
        return jsonify([{
            'id': pred.id,
            'timestamp': pred.timestamp.isoformat(),
            'predicted_churn': pred.predicted_churn,
            'churn_probability': pred.churn_probability,  # Probability included in response
            'input_data': {field: getattr(pred, field) for field in InputData.__fields__}
        } for pred in predictions])
    
    except Exception as e:
        logger.error("Failed to fetch predictions: %s", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
import React, { useState } from 'react';
import { Wifi, AlertCircle, Users, Signal, ArrowRight, ArrowLeft, RotateCcw } from 'lucide-react';

interface FormData {
  total_unsuccessful_calls: number | '';
  CustomerServiceInteractionRatio: number | '';
  MinutesOverUsage: number | '';
  TotalRevenueGenerated: number | '';
  TotalCallFeaturesUsed: number | '';
  RetentionCalls: number | '';
  RetentionOffersAccepted: number | '';
  MadeCallToRetentionTeam: number | '';
  AdjustmentsToCreditRating: number | '';
  MonthlyRevenue: number | '';
  TotalRecurringCharge: number | '';
  OverageMinutes: number | '';
  MonthsInService: number | '';
  PercChangeMinutes: number | '';
  PercChangeRevenues: number | '';
  HandsetPrice: number | '';
  CreditRating: number | '';
  IncomeGroup: number | '';
  AgeHH1: number | '';
  AgeHH2: number | '';
  ChildrenInHH: number | '';
}

interface PredictionResult {
  predicted_churn: number;
  churn_probability: number;
}

const initialFormData: FormData = {
  total_unsuccessful_calls: '',
  CustomerServiceInteractionRatio: '',
  MinutesOverUsage: '',
  TotalRevenueGenerated: '',
  TotalCallFeaturesUsed: '',
  RetentionCalls: '',
  RetentionOffersAccepted: '',
  MadeCallToRetentionTeam: '',
  AdjustmentsToCreditRating: '',
  MonthlyRevenue: '',
  TotalRecurringCharge: '',
  OverageMinutes: '',
  MonthsInService: '',
  PercChangeMinutes: '',
  PercChangeRevenues: '',
  HandsetPrice: '',
  CreditRating: '',
  IncomeGroup: '',
  AgeHH1: '',
  AgeHH2: '',
  ChildrenInHH: ''
};

const fieldDescriptions: { [key: string]: string } = {
  total_unsuccessful_calls: "Number of dropped connections or failed service attempts",
  CustomerServiceInteractionRatio: "Frequency of customer service contacts relative to service duration",
  MinutesOverUsage: "Data usage exceeding plan limits (in GB)",
  TotalRevenueGenerated: "Total revenue from the customer to date",
  TotalCallFeaturesUsed: "Number of additional services utilized (e.g., static IP, premium support)",
  RetentionCalls: "Number of calls to retention department",
  RetentionOffersAccepted: "Number of retention offers customer accepted",
  MadeCallToRetentionTeam: "Whether customer contacted retention team (0/1)",
  AdjustmentsToCreditRating: "Number of billing adjustments made",
  MonthlyRevenue: "Current monthly revenue from customer",
  TotalRecurringCharge: "Base monthly service charge",
  OverageMinutes: "Additional data usage charges",
  MonthsInService: "Duration of service in months",
  PercChangeMinutes: "Percentage change in data usage",
  PercChangeRevenues: "Percentage change in revenue",
  HandsetPrice: "Cost of equipment (router/modem)",
  CreditRating: "Customer credit score category (1-5)",
  IncomeGroup: "Income bracket (1-5)",
  AgeHH1: "Age of primary account holder",
  AgeHH2: "Age of secondary account holder (if applicable)",
  ChildrenInHH: "Number of children in household"
};

const fieldGroups = [
  {
    title: "Service Usage",
    fields: ["total_unsuccessful_calls", "MinutesOverUsage", "TotalCallFeaturesUsed", "OverageMinutes"]
  },
  {
    title: "Customer Service",
    fields: ["CustomerServiceInteractionRatio", "RetentionCalls", "RetentionOffersAccepted", "MadeCallToRetentionTeam"]
  },
  {
    title: "Financial Information",
    fields: ["TotalRevenueGenerated", "MonthlyRevenue", "TotalRecurringCharge", "AdjustmentsToCreditRating"]
  },
  {
    title: "Service History",
    fields: ["MonthsInService", "PercChangeMinutes", "PercChangeRevenues", "HandsetPrice"]
  },
  {
    title: "Customer Profile",
    fields: ["CreditRating", "IncomeGroup", "AgeHH1", "AgeHH2", "ChildrenInHH"]
  }
];

const fieldConstraints: { [key: string]: { min?: number; max?: number } } = {
  total_unsuccessful_calls: { min: 0 },
  CustomerServiceInteractionRatio: { min: 0, max: 1 },
  MinutesOverUsage: { min: 0 },
  TotalRevenueGenerated: { min: 0 },
  TotalCallFeaturesUsed: { min: 0 },
  RetentionCalls: { min: 0 },
  RetentionOffersAccepted: { min: 0 },
  MadeCallToRetentionTeam: { min: 0, max: 1 },
  AdjustmentsToCreditRating: { min: 0 },
  MonthlyRevenue: { min: 0 },
  TotalRecurringCharge: { min: 0 },
  OverageMinutes: { min: 0 },
  MonthsInService: { min: 0 },
  PercChangeMinutes: { min: -100, max: 100 },
  PercChangeRevenues: { min: -100, max: 100 },
  HandsetPrice: { min: 0 },
  CreditRating: { min: 1, max: 5 },
  IncomeGroup: { min: 1, max: 5 },
  AgeHH1: { min: 0, max: 120 },
  AgeHH2: { min: 0, max: 120 },
  ChildrenInHH: { min: 0 }
};

function App() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentGroupIndex, setCurrentGroupIndex] = useState(0);
  const [showResults, setShowResults] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    if (value === '') {
      setFormData(prev => ({
        ...prev,
        [name]: ''
      }));
      return;
    }

    const numValue = parseFloat(value);
    const constraints = fieldConstraints[name];
    
    let finalValue = numValue;
    
    if (!isNaN(numValue)) {
      if (constraints.min !== undefined && numValue < constraints.min) {
        finalValue = constraints.min;
      }
      if (constraints.max !== undefined && numValue > constraints.max) {
        finalValue = constraints.max;
      }
    } else {
      return; // Don't update if not a valid number
    }

    setFormData(prev => ({
      ...prev,
      [name]: finalValue
    }));
  };

  const handleSubmit = async () => {
    // Check if all fields have values
    const hasEmptyFields = Object.values(formData).some(value => value === '');
    if (hasEmptyFields) {
      setError('Please fill in all fields before submitting.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('https://ispmodelchurn.onrender.com/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Prediction request failed');
      }

      const result = await response.json();
      setPrediction(result);
      setShowResults(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const nextGroup = () => {
    if (currentGroupIndex < fieldGroups.length - 1) {
      setCurrentGroupIndex(prev => prev + 1);
    } else {
      handleSubmit();
    }
  };

  const prevGroup = () => {
    if (currentGroupIndex > 0) {
      setCurrentGroupIndex(prev => prev - 1);
    }
  };

  const resetForm = () => {
    setFormData(initialFormData);
    setPrediction(null);
    setCurrentGroupIndex(0);
    setShowResults(false);
    setError(null);
  };

  const getChurnRiskColor = (probability: number) => {
    if (probability < 0.3) return 'bg-green-100 text-green-800';
    if (probability < 0.7) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getRecommendedActions = (probability: number) => {
    if (probability > 0.7) {
      return {
        title: "Critical Retention Actions Required",
        steps: [
          "Analyze recent service disruptions and prepare compensation package",
          "Review competitor offers in customer's area to create a competitive counter-offer",
          "Prepare premium service upgrade proposal with first 3 months at reduced rate",
          "Document all recent customer service interactions for retention specialist review"
        ]
      };
    } else if (probability > 0.4) {
      return {
        title: "Preventive Measures Recommended",
        steps: [
          "Review service usage patterns for optimization opportunities",
          "Prepare proactive upgrade offers based on usage patterns",
          "Schedule routine check-in call within next 2 weeks",
          "Monitor service quality metrics for any degradation"
        ]
      };
    } else {
      return {
        title: "Growth Opportunity Identified",
        steps: [
          "Analyze usage patterns for premium service opportunities",
          "Include in beta testing program for new features",
          "Consider for loyalty rewards program enrollment",
          "Schedule annual service review and upgrade discussion"
        ]
      };
    }
  };

  const renderCurrentGroup = () => {
    const currentGroup = fieldGroups[currentGroupIndex];
    return (
      <div className="space-y-6 transition-all duration-500 ease-in-out">
        <h2 className="text-2xl font-semibold text-gray-900 mb-8">
          {currentGroup.title}
        </h2>
        {currentGroup.fields.map((fieldName) => (
          <div key={fieldName} className="space-y-2">
            <label className="block text-lg font-medium text-gray-700">
              {fieldName.replace(/([A-Z])/g, ' $1').trim()}
              <div className="text-sm text-gray-500 mt-1">
                {fieldDescriptions[fieldName]}
              </div>
            </label>
            <input
              type="number"
              name={fieldName}
              value={formData[fieldName as keyof FormData] === '' ? '' : formData[fieldName as keyof FormData]}
              onChange={handleInputChange}
              className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-lg transition-colors"
              placeholder="Enter value"
            />
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="max-w-3xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <div className="flex justify-center items-center space-x-3">
            <Signal className="h-12 w-12 text-blue-600" />
            <Wifi className="h-12 w-12 text-blue-600" />
          </div>
          <h1 className="mt-4 text-4xl font-bold tracking-tight text-gray-900">
            NetRetain AI
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Advanced Customer Churn Prediction for Internet Service Providers
          </p>
        </div>

        <div className="bg-white shadow-xl rounded-lg p-8 border border-gray-100">
          {!showResults ? (
            <>
              <div className="mb-8">
                <div className="flex justify-between items-center">
                  {fieldGroups.map((_, index) => (
                    <div
                      key={index}
                      className={`h-2 flex-1 mx-1 rounded ${
                        index <= currentGroupIndex ? 'bg-blue-500' : 'bg-gray-200'
                      }`}
                    />
                  ))}
                </div>
                <p className="text-center text-sm text-gray-500 mt-2">
                  Step {currentGroupIndex + 1} of {fieldGroups.length}
                </p>
              </div>

              {renderCurrentGroup()}

              <div className="mt-8 flex justify-between">
                <button
                  type="button"
                  onClick={prevGroup}
                  disabled={currentGroupIndex === 0}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <ArrowLeft className="mr-2 h-5 w-5" />
                  Previous
                </button>
                <button
                  type="button"
                  onClick={nextGroup}
                  disabled={loading}
                  className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </>
                  ) : (
                    <>
                      {currentGroupIndex === fieldGroups.length - 1 ? (
                        <>
                          <Users className="mr-2 h-5 w-5" />
                          Predict Churn
                        </>
                      ) : (
                        <>
                          Next
                          <ArrowRight className="ml-2 h-5 w-5" />
                        </>
                      )}
                    </>
                  )}
                </button>
              </div>
            </>
          ) : (
            <div className="space-y-8">
              {error ? (
                <div className="rounded-md bg-red-50 p-4">
                  <div className="flex">
                    <AlertCircle className="h-5 w-5 text-red-400" />
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">Error</h3>
                      <div className="mt-2 text-sm text-red-700">{error}</div>
                    </div>
                  </div>
                </div>
              ) : prediction && (
                <>
                  <div className="text-center">
                    <h2 className="text-3xl font-bold text-gray-900 mb-4">
                      Customer Insights
                    </h2>
                    <div className={`inline-flex items-center px-4 py-2 rounded-full text-lg font-medium mb-6 ${getChurnRiskColor(prediction.churn_probability)}`}>
                      {prediction.predicted_churn === 1 ? 'High Risk of Churn' : 'Low Risk of Churn'}
                    </div>
                  </div>

                  <div className="grid gap-6">
                    <div className="p-6 bg-white rounded-lg shadow-lg border border-gray-100">
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">
                        Churn Probability
                      </h3>
                      <div className="relative pt-1">
                        <div className="overflow-hidden h-6 text-xs flex rounded-full bg-gray-100">
                          <div
                            style={{ width: `${prediction.churn_probability * 100}%` }}
                            className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${
                              getChurnRiskColor(prediction.churn_probability).replace('bg-', 'bg-opacity-75 bg-')
                            }`}
                          />
                        </div>
                        <p className="mt-2 text-2xl font-bold text-gray-900">
                          {(prediction.churn_probability * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>

                    {/* New Recommended Actions UI */}
                    <div className="p-6 bg-white rounded-lg shadow-lg border border-gray-100">
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">
                        {getRecommendedActions(prediction.churn_probability).title}
                      </h3>
                      
                      

                      {/* Action Steps */}
                      <div className="space-y-3">
                        <h4 className="font-semibold text-gray-900 mb-3">Action Plan:</h4>
                        {getRecommendedActions(prediction.churn_probability).steps.map((step, index) => (
                          <div key={index} className="flex items-start space-x-3">
                            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-semibold text-sm">
                              {index + 1}
                            </div>
                            <p className="text-gray-700">{step}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="mt-8 flex justify-center">
                    <button
                      onClick={resetForm}
                      className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <RotateCcw className="mr-2 h-5 w-5" />
                      Analyze Another Customer
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
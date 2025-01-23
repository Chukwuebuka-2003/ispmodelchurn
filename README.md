

# 📡 ISP Customer Churn Prediction

This repository contains a machine learning project aimed at predicting customer churn for an Internet Service Provider (ISP). 🛠️ Accurately identifying customers who are likely to leave the service enables the ISP to implement targeted retention strategies. 🎯

## 📋 Project Overview

The project involves:
- 🧹 **Data Preprocessing**
- 🔍 **Exploratory Data Analysis**
- ⚙️ **Feature Engineering**
- 🧠 **Model Training and Evaluation**

Two machine learning models were developed:
1. 📈 **Logistic Regression Model**
2. 🚀 **XGBoost Model**

Both models are saved as serialized objects (`.sav` files) for deployment purposes.

---

## 📂 Repository Structure

```
├── app.py               # Flask application to serve the prediction model 🌐
├── project/               # A Vite and React frontend that interacts with the backend api 🌐
├── cell2celltrain.csv    # Dataset used for training the models 📊
├── lr_model.sav          # Serialized Logistic Regression model 📈
├── minmax_scaler.sav     # Serialized MinMaxScaler used for feature scaling 🔄
├── model.ipynb           # Jupyter Notebook for model development 📓
├── requirements.txt      # Python dependencies 📦
├── test.ipynb            # Jupyter Notebook for model testing 📓
├── wsgi.py               # Entry point for deploying the Flask application 🚀
└── xgboost_model.sav     # Serialized XGBoost model 🚀
```

---

## 🚀 Getting Started

To run this project locally, follow these steps:

### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/Chukwuebuka-2003/ispmodelchurn.git
cd ispmodelchurn
```

### 2️⃣ **Create and Activate a Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3️⃣ **Install the Required Packages**
```bash
pip install -r requirements.txt
```

### 4️⃣ **Run the Flask Application**
```bash
python app.py
```

### 5️⃣ **Access the Application**
🌐 Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🛠️ Usage

The web application allows users to input customer data and receive a prediction on whether the customer is likely to churn. 🔄 Predictions are powered by the trained Logistic Regression and XGBoost models.

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🙌 Acknowledgments

Special thanks to:
- 🧑‍💻 Contributors of this project
- 📊 Providers of the dataset used for training the models

---

🔗 **For more information, visit the [project repository](https://github.com/Chukwuebuka-2003/ispmodelchurn).**

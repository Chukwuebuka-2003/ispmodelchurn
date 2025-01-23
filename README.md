
# 📡 ISP Customer Churn Prediction

This repository contains a machine learning project aimed at predicting customer churn for an Internet Service Provider (ISP). 🛠️ Accurately identifying customers who are likely to leave the service enables the ISP to implement targeted retention strategies. 🎯

👉 **Live Frontend Website**: [ISP Churn Prediction Frontend](https://ispmodelchurn.vercel.app/) 🌐

---

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

The system comprises:
- A **Flask Backend API** to serve the prediction models.
- A **Vite React Frontend** (located in the `project/` directory) for user interaction and visualization.

---

## 📂 Repository Structure

```
├── app.py               # Flask backend API for serving predictions 🌐
├── project/             # Vite React frontend for interacting with the backend 🎨
│   ├── public/          # Public assets for the frontend 🌟
│   ├── src/             # React application source code ⚛️
│   ├── vite.config.js   # Vite configuration file 🛠️
│   └── package.json     # Frontend dependencies and scripts 📦
├── cell2celltrain.csv   # Dataset used for training the models 📊
├── lr_model.sav         # Serialized Logistic Regression model 📈
├── minmax_scaler.sav    # Serialized MinMaxScaler used for feature scaling 🔄
├── model.ipynb          # Jupyter Notebook for model development 📓
├── requirements.txt     # Python backend dependencies 📦
├── test.ipynb           # Jupyter Notebook for model testing 📓
├── wsgi.py              # Entry point for deploying the Flask application 🚀
└── xgboost_model.sav    # Serialized XGBoost model 🚀
```

---

## 🚀 Getting Started

To run this project locally, follow these steps:

### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/Chukwuebuka-2003/ispmodelchurn.git
cd ispmodelchurn
```

### 2️⃣ **Set Up the Backend API**
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask application:
   ```bash
   python app.py
   ```
4. The API will be available at:
   ```
   http://localhost:5000
   ```

### 3️⃣ **Set Up the Frontend**
1. Navigate to the `project/` directory:
   ```bash
   cd project
   ```
2. Install frontend dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. The frontend will be available at:
   ```
   http://localhost:5173
   ```

---

## 🛠️ Usage

1. Use the **Frontend Website** to input customer data.  
2. The frontend interacts with the **Flask API** to send data and receive churn predictions.  
3. View results and analyze customer churn likelihood.  

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
🔗 **Frontend Website**: [ISP Churn Prediction Frontend](https://ispmodelchurn.vercel.app/) 🌐

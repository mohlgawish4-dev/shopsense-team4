# Cart Abandonment Prediction

## Overview

A machine learning model that predicts whether an e-commerce
shopping session results in a purchase or no purchase.

For this project, a no-purchase prediction is used as an
abandonment proxy.

## Model

XGBoost Classifier

A Logistic Regression model was also trained as a baseline.

## Dataset

UCI Online Shoppers Purchasing Intention Dataset.

The target variable is `Revenue`:
- 1 → Purchase
- 0 → No Purchase

## Pipeline

Dataset
→ Data preprocessing
→ One-hot encoding
→ Train/Test Split
→ Logistic Regression baseline
→ XGBoost
→ Evaluation
→ Saved model
→ Flask API

## Files

- `cart_abandonment.ipynb` — training and experiments
- `model.pkl` — trained XGBoost model
- `api.py` — Flask API
- `requirements.txt` — dependencies

## API

### POST /predict

The API receives the session features as JSON and returns a prediction.

Example response:

```json
{
    "status": "success",
    "prediction": 0,
    "cart_abandoned": true
}# cart-abandonment-prediction

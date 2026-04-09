"""Project-wide configuration and constants."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
MLRUNS_DIR = PROJECT_ROOT / "mlruns"
MLARTIFACTS_DIR = PROJECT_ROOT / "mlartifacts"
MLFLOW_DB_PATH = PROJECT_ROOT / "mlflow.db"
MLFLOW_TRACKING_URI = f"sqlite:///{MLFLOW_DB_PATH.resolve()}"

RAW_DATA_FILENAME = "BankChurners.csv"
PROCESSED_DATA_FILENAME = "bank_churners_processed.csv"
TRAINING_BASELINE_FILENAME = "training_baseline.csv"
SERIALIZED_MODEL_FILENAME = "churn_model.joblib"
METADATA_FILENAME = "model_metadata.json"

TARGET_COLUMN = "Attrition_Flag"
TARGET_MAPPING = {
    "Existing Customer": 0,
    "Attrited Customer": 1,
}
DROP_COLUMNS = [
    "CLIENTNUM",
]
NAIVE_BAYES_PREFIX = "Naive_Bayes_Classifier"

NUMERICAL_FEATURES = [
    "Customer_Age",
    "Dependent_count",
    "Months_on_book",
    "Total_Relationship_Count",
    "Months_Inactive_12_mon",
    "Contacts_Count_12_mon",
    "Credit_Limit",
    "Total_Revolving_Bal",
    "Avg_Open_To_Buy",
    "Total_Amt_Chng_Q4_Q1",
    "Total_Trans_Amt",
    "Total_Trans_Ct",
    "Total_Ct_Chng_Q4_Q1",
    "Avg_Utilization_Ratio",
]

CATEGORICAL_FEATURES = [
    "Gender",
    "Education_Level",
    "Marital_Status",
    "Income_Category",
    "Card_Category",
]

FEATURE_COLUMNS = NUMERICAL_FEATURES + CATEGORICAL_FEATURES

EXPECTED_COLUMNS = FEATURE_COLUMNS + [TARGET_COLUMN]

NUMERIC_RANGES = {
    "Customer_Age": (18, 100),
    "Dependent_count": (0, 20),
    "Months_on_book": (0, 120),
    "Total_Relationship_Count": (0, 20),
    "Months_Inactive_12_mon": (0, 12),
    "Contacts_Count_12_mon": (0, 20),
    "Credit_Limit": (0, 1_000_000),
    "Total_Revolving_Bal": (0, 1_000_000),
    "Avg_Open_To_Buy": (0, 1_000_000),
    "Total_Amt_Chng_Q4_Q1": (0, 100),
    "Total_Trans_Amt": (0, 10_000_000),
    "Total_Trans_Ct": (0, 10_000),
    "Total_Ct_Chng_Q4_Q1": (0, 100),
    "Avg_Utilization_Ratio": (0, 1),
}

MODEL_NAME = "credit-card-churn-model"
EXPERIMENT_NAME = "customer-churn-prediction"

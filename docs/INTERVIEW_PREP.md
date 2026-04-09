# Interview Prep

## 30-Second Summary

I built an end-to-end churn prediction system for the BankChurners dataset that simulates a production ML workflow. The project covers ingestion, data validation, preprocessing pipelines, multi-model training, MLflow experiment tracking and model registry, FastAPI serving, persistent online inference metrics, data drift detection, and retraining triggers.

## Problem Statement

The goal was to predict whether a customer is likely to churn, using credit card customer behavior and profile features. Instead of building only a notebook, I designed the project like a deployable ML system.

## What Makes It Production-Style

- Separate modules for ingestion, validation, training, evaluation, inference, and monitoring
- Reusable sklearn preprocessing pipeline shared between training and serving
- MLflow-backed experiment tracking and model registry
- API-based inference with request validation
- Persistent online serving metrics stored in SQLite
- Drift detection with retraining hook
- Makefile and startup scripts for local operations

## ML Lifecycle Mapping

### 1. Data ingestion

- Load raw CSV
- Drop identifier and leakage-prone columns
- Convert target labels to binary
- Save a processed artifact

### 2. Data validation

- Enforce schema with Pandera
- Check required columns, types, null constraints, and numeric ranges
- Fail early on bad data

### 3. Feature engineering

- Numerical: median imputation + standard scaling
- Categorical: most-frequent imputation + one-hot encoding
- Combined with `ColumnTransformer`

### 4. Training

- Train Logistic Regression, Random Forest, and XGBoost
- Compare them on classification metrics
- Select best model by ROC-AUC

### 5. Experiment tracking

- Log parameters, metrics, and model artifacts to MLflow
- Register best model in MLflow Model Registry

### 6. Deployment

- Serialize full preprocessing + model pipeline with joblib
- Serve predictions through FastAPI

### 7. Monitoring

- Persist request-level serving metrics like latency, errors, and prediction mix
- Expose dashboard and JSON endpoint

### 8. Post-deployment maintenance

- Compare baseline training data to new production data with KS test
- Trigger retraining when drift is detected

## Design Decisions To Explain

### Why remove `CLIENTNUM`?

It is an identifier, not a predictive business feature.

### Why drop `Naive_Bayes_Classifier` columns?

Those are derived outputs and can introduce leakage.

### Why use ROC-AUC to select the best model?

This is a churn classification problem where ranking risk matters more than plain accuracy.

### Why keep preprocessing inside the pipeline?

It prevents train/serve skew and makes the saved artifact directly deployable.

### Why compare three model families first instead of tuning immediately?

I wanted a strong baseline system covering the full lifecycle first, then leave room for future hyperparameter optimization.

### Why use both MLflow and a serving metrics DB?

MLflow tracks training lifecycle and model lineage. The serving metrics DB tracks operational inference behavior like latency and failures.

## Likely Interview Questions

### How is the best model chosen?

The current system trains one configured version each of Logistic Regression, Random Forest, and XGBoost, then picks the model with the highest ROC-AUC on the holdout test set.

### Are hyperparameters tuned?

Not yet. Each candidate model currently uses one fixed configuration. A next step would be `GridSearchCV`, `RandomizedSearchCV`, or Optuna with cross-validation.

### What would you improve next?

- Add validation split or cross-validation for model selection
- Add hyperparameter search
- Persist prediction inputs for offline label join and production performance tracking
- Add Docker and CI/CD
- Add authentication and proper observability stack

### What production risks still remain?

- Current serving metrics are local SQLite, not centralized observability
- Drift detection uses only numerical features
- Retraining is synchronous and local, not scheduled/orchestrated
- No containerized deployment or infra automation yet

## One-Minute Walkthrough

I start by ingesting and cleaning the BankChurners data, removing non-useful and leakage-prone columns. Then I validate the schema with Pandera so bad data fails fast. I use a sklearn preprocessing pipeline with imputation, scaling, and one-hot encoding so the same logic is used in both training and inference. I train Logistic Regression, Random Forest, and XGBoost, evaluate them on multiple metrics, and select the best model by ROC-AUC. Every run is logged to MLflow, and the best model is registered. For deployment, I save the whole pipeline with joblib and serve it via FastAPI. On top of that, I built persistent online serving metrics and a dashboard to monitor request count, errors, latency, and prediction distribution. I also added drift detection with a KS test and a retraining trigger to show the post-deployment ML lifecycle.

## Resume Bullet

Built a production-style customer churn prediction system with schema validation, sklearn feature pipelines, MLflow experiment tracking and registry, FastAPI inference, persistent serving metrics, drift detection, and retraining hooks.

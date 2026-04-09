# Hugging Face Deployment App

This folder contains the minimal inference-only app for deploying the churn project to Hugging Face Spaces.

## Included

- `api/`: FastAPI app, UI, and serving metrics dashboard
- `pipeline/inference_pipeline.py`: model loading and prediction logic
- `src/config.py`: runtime configuration
- `models/churn_model.joblib`: serialized production model pipeline
- `models/model_metadata.json`: model summary metadata
- `requirements.txt`: Python dependencies
- `Dockerfile`: container startup for Hugging Face Spaces

## Excluded On Purpose

- training pipeline
- MLflow tracking setup
- drift monitoring
- notebooks
- tests
- raw and processed datasets

This deployment app is only for hosted inference and demo purposes.

## Expected Routes

- `/`: prediction UI
- `/dashboard`: serving metrics dashboard
- `/docs`: FastAPI docs
- `/predict`: inference API

## Deploy To Hugging Face

1. Create a new Hugging Face Space
2. Choose `Docker` SDK
3. Push only the contents of this `hf_app/` folder to the Space repo

The full GitHub repository remains the project showcase. This folder is the stripped-down deployable runtime.

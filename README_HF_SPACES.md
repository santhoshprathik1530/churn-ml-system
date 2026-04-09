# Hugging Face Spaces Deployment

This project can be deployed to Hugging Face Spaces as a Docker app.

## Recommended Space Settings

- SDK: `Docker`
- Visibility: Public
- Hardware: Free CPU basic is enough for this demo

## What the deployed app includes

- prediction UI at `/`
- metrics dashboard at `/dashboard`
- FastAPI docs at `/docs`

## Deployment Steps

1. Create a new Hugging Face Space
2. Choose `Docker` as the SDK
3. Upload this repository or connect it from GitHub
4. Make sure the repo includes:
   - `data/raw/BankChurners.csv`
   - `models/churn_model.joblib`
   - `models/model_metadata.json`
5. Let the Docker build finish
6. Open the public Space URL

## Notes

- MLflow is intentionally not deployed in the Space
- the Space is only for the FastAPI demo app
- if the Space restarts, local runtime metrics may reset depending on the platform storage behavior

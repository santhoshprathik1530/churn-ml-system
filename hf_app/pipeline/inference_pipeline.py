"""Inference pipeline for batch or online scoring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.config import FEATURE_COLUMNS, MODELS_DIR, SERIALIZED_MODEL_FILENAME


def load_model(model_path: Path | None = None) -> Any:
    """Load the serialized churn model pipeline."""
    path = model_path or (MODELS_DIR / SERIALIZED_MODEL_FILENAME)
    if not path.exists():
        raise FileNotFoundError(
            f"Serialized model not found at {path}. Run training first."
        )
    return joblib.load(path)


def prepare_inference_frame(payload: dict[str, Any]) -> pd.DataFrame:
    """Convert request payload into a model-ready dataframe."""
    missing_features = sorted(set(FEATURE_COLUMNS) - set(payload.keys()))
    if missing_features:
        raise ValueError(f"Missing inference features: {missing_features}")
    ordered_payload = {column: payload[column] for column in FEATURE_COLUMNS}
    return pd.DataFrame([ordered_payload])


def predict(
    payload: dict[str, Any],
    model_path: Path | None = None,
) -> dict[str, float | int]:
    """Generate churn prediction and probability."""
    model = load_model(model_path)
    features = prepare_inference_frame(payload)
    prediction = int(model.predict(features)[0])
    probability = float(model.predict_proba(features)[0, 1])
    return {
        "prediction": prediction,
        "probability": probability,
    }

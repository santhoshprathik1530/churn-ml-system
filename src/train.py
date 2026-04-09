"""Model training and MLflow integration."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient
from sklearn.base import ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from src.config import (
    EXPERIMENT_NAME,
    FEATURE_COLUMNS,
    METADATA_FILENAME,
    MLARTIFACTS_DIR,
    MLFLOW_TRACKING_URI,
    MODEL_NAME,
    MODELS_DIR,
    SERIALIZED_MODEL_FILENAME,
    TARGET_COLUMN,
    TRAINING_BASELINE_FILENAME,
)
from src.evaluate import build_evaluation_summary, compute_classification_metrics
from src.feature_pipeline import build_preprocessing_pipeline


@dataclass
class TrainingArtifacts:
    """Artifacts produced by training."""

    best_model_name: str
    best_metrics: dict[str, float]
    best_run_id: str
    registered_model_version: str | None
    serialized_model_path: Path
    baseline_data_path: Path
    metadata_path: Path
    test_metrics_by_model: dict[str, dict[str, float]]


def create_model_candidates(random_state: int = 42) -> dict[str, ClassifierMixin]:
    """Instantiate candidate estimators."""
    return {
        "logistic_regression": LogisticRegression(
            max_iter=1_000,
            solver="lbfgs",
            class_weight="balanced",
            random_state=random_state,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=12,
            min_samples_leaf=2,
            n_jobs=-1,
            class_weight="balanced",
            random_state=random_state,
        ),
        "xgboost": XGBClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=random_state,
        ),
    }


def _extract_model_params(model: ClassifierMixin) -> dict[str, Any]:
    params = model.get_params()
    simple_types = (str, int, float, bool, type(None))
    return {
        key: value
        for key, value in params.items()
        if isinstance(value, simple_types)
    }


def _set_mlflow_tracking() -> None:
    MLARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, "-m", "mlflow", "db", "upgrade", MLFLOW_TRACKING_URI],
        check=True,
        capture_output=True,
        text=True,
    )
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        artifact_location = (MLARTIFACTS_DIR / EXPERIMENT_NAME).resolve().as_uri()
        experiment_id = client.create_experiment(
            name=EXPERIMENT_NAME,
            artifact_location=artifact_location,
        )
        mlflow.set_experiment(experiment_id=experiment_id)
    else:
        mlflow.set_experiment(experiment_name=EXPERIMENT_NAME)


def _build_model_pipeline(model: ClassifierMixin) -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessing_pipeline()),
            ("model", model),
        ]
    )


def _register_best_model(model_uri: str, run_id: str) -> str | None:
    client = MlflowClient()
    try:
        registered_model = mlflow.register_model(model_uri=model_uri, name=MODEL_NAME)
        client.transition_model_version_stage(
            name=MODEL_NAME,
            version=registered_model.version,
            stage="Production",
            archive_existing_versions=True,
        )
        client.set_model_version_tag(
            name=MODEL_NAME,
            version=registered_model.version,
            key="source_run_id",
            value=run_id,
        )
        return str(registered_model.version)
    except Exception:
        return None


def _save_serialized_assets(
    trained_pipeline: Pipeline,
    training_features: pd.DataFrame,
    metadata: dict[str, Any],
) -> tuple[Path, Path, Path]:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    serialized_model_path = MODELS_DIR / SERIALIZED_MODEL_FILENAME
    baseline_data_path = MODELS_DIR / TRAINING_BASELINE_FILENAME
    metadata_path = MODELS_DIR / METADATA_FILENAME

    joblib.dump(trained_pipeline, serialized_model_path)
    training_features.to_csv(baseline_data_path, index=False)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return serialized_model_path, baseline_data_path, metadata_path


def train_and_track_models(
    dataframe: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42,
) -> TrainingArtifacts:
    """Train candidate models, log runs, and register the best model."""
    _set_mlflow_tracking()

    X = dataframe[FEATURE_COLUMNS]
    y = dataframe[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        stratify=y,
        random_state=random_state,
    )

    candidates = create_model_candidates(random_state=random_state)
    best_model_name = ""
    best_metrics: dict[str, float] = {}
    best_pipeline: Pipeline | None = None
    best_run_id = ""
    best_score = float("-inf")
    test_metrics_by_model: dict[str, dict[str, float]] = {}

    for model_name, estimator in candidates.items():
        pipeline = _build_model_pipeline(estimator)
        params = _extract_model_params(estimator)
        with mlflow.start_run(run_name=model_name) as run:
            pipeline.fit(X_train, y_train)
            predictions = pipeline.predict(X_test)
            probabilities = pipeline.predict_proba(X_test)[:, 1]
            metrics = compute_classification_metrics(
                y_true=np.asarray(y_test),
                y_pred=np.asarray(predictions),
                y_proba=np.asarray(probabilities),
            )
            test_metrics_by_model[model_name] = metrics

            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            signature = infer_signature(X_train, pipeline.predict(X_train))
            mlflow.sklearn.log_model(
                sk_model=pipeline,
                artifact_path="model",
                signature=signature,
                registered_model_name=None,
            )
            evaluation_summary = build_evaluation_summary(model_name, metrics, params)
            mlflow.log_dict(evaluation_summary, "evaluation_summary.json")

            if metrics["roc_auc"] > best_score:
                best_score = metrics["roc_auc"]
                best_model_name = model_name
                best_metrics = metrics
                best_pipeline = pipeline
                best_run_id = run.info.run_id

    if best_pipeline is None:
        raise RuntimeError("Model training did not produce a best pipeline.")

    model_uri = f"runs:/{best_run_id}/model"
    registered_version = _register_best_model(model_uri=model_uri, run_id=best_run_id)

    metadata = {
        "best_model_name": best_model_name,
        "best_run_id": best_run_id,
        "registered_model_version": registered_version,
        "metrics": best_metrics,
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
    }
    serialized_model_path, baseline_data_path, metadata_path = _save_serialized_assets(
        trained_pipeline=best_pipeline,
        training_features=X_train,
        metadata=metadata,
    )

    return TrainingArtifacts(
        best_model_name=best_model_name,
        best_metrics=best_metrics,
        best_run_id=best_run_id,
        registered_model_version=registered_version,
        serialized_model_path=serialized_model_path,
        baseline_data_path=baseline_data_path,
        metadata_path=metadata_path,
        test_metrics_by_model=test_metrics_by_model,
    )

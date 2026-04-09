"""Orchestrates the training workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.ingestion import clean_data, load_data, save_processed_data
from src.train import train_and_track_models
from src.validation import summarize_schema, validate_data


def run_training_pipeline(raw_data_path: Path | None = None) -> dict[str, Any]:
    """Run ingestion, validation, training, logging, and model registration."""
    raw_df = load_data(raw_data_path)
    cleaned_df = clean_data(raw_df)
    processed_path = save_processed_data(cleaned_df)
    validated_df = validate_data(cleaned_df)
    schema_summary = summarize_schema(validated_df)
    training_artifacts = train_and_track_models(validated_df)

    return {
        "processed_data_path": str(processed_path),
        "schema_summary": schema_summary,
        "best_model_name": training_artifacts.best_model_name,
        "best_metrics": training_artifacts.best_metrics,
        "best_run_id": training_artifacts.best_run_id,
        "registered_model_version": training_artifacts.registered_model_version,
        "serialized_model_path": str(training_artifacts.serialized_model_path),
        "baseline_data_path": str(training_artifacts.baseline_data_path),
        "metadata_path": str(training_artifacts.metadata_path),
        "test_metrics_by_model": training_artifacts.test_metrics_by_model,
    }


if __name__ == "__main__":
    results = run_training_pipeline()
    print(results)

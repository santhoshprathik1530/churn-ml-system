"""Data drift detection and retraining trigger logic."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from scipy.stats import ks_2samp

from pipeline.training_pipeline import run_training_pipeline
from src.config import FEATURE_COLUMNS, NUMERICAL_FEATURES


def detect_drift(
    reference_data: pd.DataFrame,
    new_data: pd.DataFrame,
    p_value_threshold: float = 0.05,
) -> dict[str, Any]:
    """Compare feature distributions using the KS test for numerical features."""
    per_feature_report: dict[str, dict[str, float | bool]] = {}
    drift_detected = False

    for feature in NUMERICAL_FEATURES:
        statistic, p_value = ks_2samp(
            reference_data[feature].dropna(),
            new_data[feature].dropna(),
        )
        feature_drift = bool(p_value < p_value_threshold)
        per_feature_report[feature] = {
            "ks_statistic": float(statistic),
            "p_value": float(p_value),
            "drift_detected": feature_drift,
        }
        drift_detected = drift_detected or feature_drift

    return {
        "overall_drift_detected": drift_detected,
        "threshold": p_value_threshold,
        "features_checked": FEATURE_COLUMNS,
        "numerical_feature_report": per_feature_report,
    }


def maybe_retrain_on_drift(
    reference_data: pd.DataFrame,
    new_data: pd.DataFrame,
    raw_data_path: Path | None = None,
    p_value_threshold: float = 0.05,
) -> dict[str, Any]:
    """Trigger retraining automatically if drift is detected."""
    drift_report = detect_drift(
        reference_data=reference_data,
        new_data=new_data,
        p_value_threshold=p_value_threshold,
    )
    if drift_report["overall_drift_detected"]:
        retraining_result = run_training_pipeline(raw_data_path=raw_data_path)
        drift_report["retraining_triggered"] = True
        drift_report["retraining_result"] = retraining_result
    else:
        drift_report["retraining_triggered"] = False
    return drift_report

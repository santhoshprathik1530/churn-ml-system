"""Model evaluation helpers."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray,
) -> dict[str, float]:
    """Compute the core classification metrics used across experiments."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
    }


def build_evaluation_summary(
    model_name: str,
    metrics: dict[str, float],
    params: dict[str, Any],
) -> dict[str, Any]:
    """Compose a normalized evaluation artifact."""
    return {
        "model_name": model_name,
        "metrics": metrics,
        "params": params,
    }

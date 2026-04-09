"""SQLite-backed online serving metrics for the FastAPI app."""

from __future__ import annotations

import math
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.config import PROJECT_ROOT


SERVING_METRICS_DB = PROJECT_ROOT / "serving_metrics.db"


class OnlineMetricsStore:
    """Thread-safe persistent store for online serving metrics."""

    def __init__(self, db_path: Path = SERVING_METRICS_DB) -> None:
        self._lock = threading.Lock()
        self.db_path = db_path
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS request_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    prediction INTEGER,
                    probability REAL,
                    error_message TEXT
                )
                """
            )
            connection.commit()

    def record_success(
        self,
        latency_ms: float,
        prediction: int,
        probability: float,
    ) -> None:
        """Persist a successful prediction request."""
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO request_logs (
                    timestamp,
                    status,
                    latency_ms,
                    prediction,
                    probability,
                    error_message
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(UTC).isoformat(),
                    "success",
                    float(latency_ms),
                    int(prediction),
                    float(probability),
                    None,
                ),
            )
            connection.commit()

    def record_failure(self, latency_ms: float, error_message: str) -> None:
        """Persist a failed prediction request."""
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO request_logs (
                    timestamp,
                    status,
                    latency_ms,
                    prediction,
                    probability,
                    error_message
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(UTC).isoformat(),
                    "failure",
                    float(latency_ms),
                    None,
                    None,
                    error_message,
                ),
            )
            connection.commit()

    def _percentile(self, values: list[float], percentile: float) -> float:
        if not values:
            return 0.0
        sorted_values = sorted(values)
        rank = math.ceil((percentile / 100) * len(sorted_values)) - 1
        rank = max(0, min(rank, len(sorted_values) - 1))
        return sorted_values[rank]

    def snapshot(self) -> dict[str, Any]:
        """Return a metrics snapshot aggregated from persisted request logs."""
        with self._lock, self._connect() as connection:
            started_at_row = connection.execute(
                "SELECT MIN(timestamp) AS started_at FROM request_logs"
            ).fetchone()
            aggregate_row = connection.execute(
                """
                SELECT
                    COUNT(*) AS total_requests,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS successful_requests,
                    SUM(CASE WHEN status = 'failure' THEN 1 ELSE 0 END) AS failed_requests,
                    AVG(latency_ms) AS avg_latency_ms,
                    MAX(latency_ms) AS max_latency_ms,
                    AVG(CASE WHEN status = 'success' THEN probability END) AS avg_probability,
                    AVG(CASE WHEN status = 'success' THEN prediction END) AS positive_prediction_rate
                FROM request_logs
                """
            ).fetchone()
            recent_rows = connection.execute(
                """
                SELECT timestamp, prediction, probability, latency_ms
                FROM request_logs
                WHERE status = 'success'
                ORDER BY id DESC
                LIMIT 20
                """
            ).fetchall()
            error_row = connection.execute(
                """
                SELECT error_message
                FROM request_logs
                WHERE status = 'failure'
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
            latency_rows = connection.execute(
                "SELECT latency_ms FROM request_logs ORDER BY id DESC LIMIT 200"
            ).fetchall()

        latencies = [float(row["latency_ms"]) for row in latency_rows]
        total_requests = int(aggregate_row["total_requests"] or 0)
        successful_requests = int(aggregate_row["successful_requests"] or 0)
        failed_requests = int(aggregate_row["failed_requests"] or 0)

        started_at = started_at_row["started_at"]
        if started_at is None:
            started_at_dt = datetime.now(UTC)
        else:
            started_at_dt = datetime.fromisoformat(started_at)

        uptime_seconds = max((datetime.now(UTC) - started_at_dt).total_seconds(), 1.0)
        success_rate = successful_requests / total_requests if total_requests else 0.0
        recent_predictions = [
            {
                "timestamp": row["timestamp"],
                "prediction": int(row["prediction"]),
                "probability": round(float(row["probability"]), 4),
                "latency_ms": round(float(row["latency_ms"]), 2),
            }
            for row in recent_rows
        ]

        return {
            "started_at": started_at_dt.isoformat(),
            "uptime_seconds": round(uptime_seconds, 2),
            "requests_per_minute": round((total_requests / uptime_seconds) * 60, 2),
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": round(success_rate, 4),
            "avg_latency_ms": round(float(aggregate_row["avg_latency_ms"] or 0.0), 2),
            "p95_latency_ms": round(self._percentile(latencies, 95), 2),
            "max_latency_ms": round(float(aggregate_row["max_latency_ms"] or 0.0), 2),
            "avg_probability": round(float(aggregate_row["avg_probability"] or 0.0), 4),
            "positive_prediction_rate": round(
                float(aggregate_row["positive_prediction_rate"] or 0.0), 4
            ),
            "last_error": error_row["error_message"] if error_row else None,
            "recent_predictions": recent_predictions,
        }


metrics_store = OnlineMetricsStore()

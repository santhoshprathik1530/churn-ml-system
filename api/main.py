"""FastAPI inference service for churn prediction."""

from __future__ import annotations

import time
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field

from api.monitoring import metrics_store
from api.ui import dashboard_page_html, prediction_page_html
from pipeline.inference_pipeline import predict

app = FastAPI(
    title="Customer Churn Prediction API",
    version="1.0.0",
    description="Production-style inference API for BankChurners churn scoring.",
)


class ChurnPredictionRequest(BaseModel):
    """Request payload for online churn scoring."""

    model_config = ConfigDict(populate_by_name=True)

    Customer_Age: int = Field(..., ge=18, le=100)
    Gender: Literal["M", "F"]
    Dependent_count: int = Field(..., ge=0, le=20)
    Education_Level: str
    Marital_Status: str
    Income_Category: str
    Card_Category: str
    Months_on_book: int = Field(..., ge=0, le=120)
    Total_Relationship_Count: int = Field(..., ge=0, le=20)
    Months_Inactive_12_mon: int = Field(..., ge=0, le=12)
    Contacts_Count_12_mon: int = Field(..., ge=0, le=20)
    Credit_Limit: float = Field(..., ge=0)
    Total_Revolving_Bal: float = Field(..., ge=0)
    Avg_Open_To_Buy: float = Field(..., ge=0)
    Total_Amt_Chng_Q4_Q1: float = Field(..., ge=0)
    Total_Trans_Amt: float = Field(..., ge=0)
    Total_Trans_Ct: int = Field(..., ge=0)
    Total_Ct_Chng_Q4_Q1: float = Field(..., ge=0)
    Avg_Utilization_Ratio: float = Field(..., ge=0, le=1)


class ChurnPredictionResponse(BaseModel):
    """Prediction response payload."""

    prediction: int
    probability: float


@app.middleware("http")
async def capture_predict_metrics(request: Request, call_next):
    """Capture online-serving telemetry for prediction traffic."""
    if request.url.path != "/predict":
        return await call_next(request)

    start_time = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        latency_ms = (time.perf_counter() - start_time) * 1000
        metrics_store.record_failure(latency_ms=latency_ms, error_message=str(exc))
        raise

    latency_ms = (time.perf_counter() - start_time) * 1000
    prediction_result = getattr(request.state, "prediction_result", None)

    if response.status_code < 400 and prediction_result is not None:
        metrics_store.record_success(
            latency_ms=latency_ms,
            prediction=prediction_result["prediction"],
            probability=prediction_result["probability"],
        )
    else:
        metrics_store.record_failure(
            latency_ms=latency_ms,
            error_message=f"HTTP {response.status_code}",
        )
    return response


@app.get("/", response_class=HTMLResponse)
def prediction_ui() -> HTMLResponse:
    """Render the interactive predictor page."""
    return HTMLResponse(content=prediction_page_html())


@app.get("/dashboard", response_class=HTMLResponse)
def metrics_dashboard() -> HTMLResponse:
    """Render the live metrics dashboard page."""
    return HTMLResponse(content=dashboard_page_html())


@app.get("/metrics/summary")
def metrics_summary() -> dict[str, object]:
    """Expose online-serving telemetry as JSON."""
    return metrics_store.snapshot()


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple health endpoint."""
    return {"status": "ok"}


@app.post("/predict", response_model=ChurnPredictionResponse)
def predict_churn(
    request: Request,
    payload: ChurnPredictionRequest,
) -> ChurnPredictionResponse:
    """Predict churn probability for a single customer."""
    try:
        result = predict(payload.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    request.state.prediction_result = result
    return ChurnPredictionResponse(**result)

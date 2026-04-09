"""Tests for inference payload preparation."""

from __future__ import annotations

import pytest

from pipeline.inference_pipeline import prepare_inference_frame


def test_prepare_inference_frame_orders_expected_features() -> None:
    payload = {
        "Customer_Age": 45,
        "Gender": "M",
        "Dependent_count": 2,
        "Education_Level": "Graduate",
        "Marital_Status": "Married",
        "Income_Category": "$60K - $80K",
        "Card_Category": "Blue",
        "Months_on_book": 36,
        "Total_Relationship_Count": 4,
        "Months_Inactive_12_mon": 1,
        "Contacts_Count_12_mon": 2,
        "Credit_Limit": 12000,
        "Total_Revolving_Bal": 800,
        "Avg_Open_To_Buy": 11200,
        "Total_Amt_Chng_Q4_Q1": 1.1,
        "Total_Trans_Amt": 4000,
        "Total_Trans_Ct": 65,
        "Total_Ct_Chng_Q4_Q1": 1.2,
        "Avg_Utilization_Ratio": 0.3,
    }

    frame = prepare_inference_frame(payload)

    assert frame.shape == (1, 19)
    assert frame.columns.tolist()[0] == "Customer_Age"


def test_prepare_inference_frame_rejects_missing_fields() -> None:
    with pytest.raises(ValueError):
        prepare_inference_frame({"Customer_Age": 45})

"""Tests for ingestion utilities."""

from __future__ import annotations

import pandas as pd

from src.ingestion import clean_data


def test_clean_data_drops_irrelevant_columns_and_maps_target() -> None:
    df = pd.DataFrame(
        {
            "CLIENTNUM": [12345],
            "Customer_Age": [45],
            "Gender": ["M"],
            "Dependent_count": [2],
            "Education_Level": ["Graduate"],
            "Marital_Status": ["Married"],
            "Income_Category": ["$60K - $80K"],
            "Card_Category": ["Blue"],
            "Months_on_book": [36],
            "Total_Relationship_Count": [4],
            "Months_Inactive_12_mon": [1],
            "Contacts_Count_12_mon": [2],
            "Credit_Limit": [12000.0],
            "Total_Revolving_Bal": [800.0],
            "Avg_Open_To_Buy": [11200.0],
            "Total_Amt_Chng_Q4_Q1": [1.1],
            "Total_Trans_Amt": [4000.0],
            "Total_Trans_Ct": [65],
            "Total_Ct_Chng_Q4_Q1": [1.2],
            "Avg_Utilization_Ratio": [0.3],
            "Attrition_Flag": ["Attrited Customer"],
            "Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_1": [0.1],
        }
    )

    cleaned = clean_data(df)

    assert "CLIENTNUM" not in cleaned.columns
    assert not any(col.startswith("Naive_Bayes_Classifier") for col in cleaned.columns)
    assert cleaned.loc[0, "Attrition_Flag"] == 1

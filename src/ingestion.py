"""Data ingestion utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import (
    DROP_COLUMNS,
    NAIVE_BAYES_PREFIX,
    PROCESSED_DATA_DIR,
    PROCESSED_DATA_FILENAME,
    RAW_DATA_DIR,
    RAW_DATA_FILENAME,
    TARGET_COLUMN,
    TARGET_MAPPING,
)


def load_data(file_path: Path | None = None) -> pd.DataFrame:
    """Load raw churn data from CSV."""
    dataset_path = file_path or (RAW_DATA_DIR / RAW_DATA_FILENAME)
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {dataset_path}. "
            f"Place {RAW_DATA_FILENAME} under {RAW_DATA_DIR}."
        )
    return pd.read_csv(dataset_path)


def clean_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Drop irrelevant columns and convert the target to binary."""
    df = dataframe.copy()
    drop_columns = DROP_COLUMNS + [
        column for column in df.columns if column.startswith(NAIVE_BAYES_PREFIX)
    ]
    df = df.drop(columns=drop_columns, errors="ignore")
    if TARGET_COLUMN not in df.columns:
        raise KeyError(f"Expected target column '{TARGET_COLUMN}' was not found.")
    df[TARGET_COLUMN] = df[TARGET_COLUMN].replace(TARGET_MAPPING)
    if df[TARGET_COLUMN].isna().any():
        invalid_values = dataframe.loc[
            ~dataframe[TARGET_COLUMN].isin(TARGET_MAPPING.keys()), TARGET_COLUMN
        ].unique()
        raise ValueError(
            "Unexpected target values encountered: "
            + ", ".join(map(str, invalid_values))
        )
    df[TARGET_COLUMN] = df[TARGET_COLUMN].astype(int)
    return df


def save_processed_data(
    dataframe: pd.DataFrame,
    output_path: Path | None = None,
) -> Path:
    """Persist cleaned data to the processed data directory."""
    destination = output_path or (PROCESSED_DATA_DIR / PROCESSED_DATA_FILENAME)
    destination.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(destination, index=False)
    return destination


def run_ingestion(
    input_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    """Execute ingestion end-to-end."""
    raw_df = load_data(input_path)
    cleaned_df = clean_data(raw_df)
    return save_processed_data(cleaned_df, output_path)


if __name__ == "__main__":
    processed_path = run_ingestion()
    print(f"Processed data saved to: {processed_path}")

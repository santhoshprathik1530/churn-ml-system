"""Data validation with Pandera."""

from __future__ import annotations

from typing import Any

import pandas as pd
import pandera as pa
from pandera import Check, Column, DataFrameSchema

from src.config import CATEGORICAL_FEATURES, EXPECTED_COLUMNS, NUMERIC_RANGES, TARGET_COLUMN


def build_schema() -> DataFrameSchema:
    """Construct the validation schema for the cleaned dataset."""
    schema_columns: dict[str, Column] = {}

    for column_name, (min_value, max_value) in NUMERIC_RANGES.items():
        schema_columns[column_name] = Column(
            float,
            nullable=False,
            coerce=True,
            checks=[Check.in_range(min_value, max_value)],
        )

    for column_name in CATEGORICAL_FEATURES:
        schema_columns[column_name] = Column(
            str,
            nullable=False,
            coerce=True,
            checks=[Check.str_length(min_value=1)],
        )

    schema_columns[TARGET_COLUMN] = Column(
        int,
        nullable=False,
        coerce=True,
        checks=[Check.isin([0, 1])],
    )

    return DataFrameSchema(
        columns=schema_columns,
        strict=True,
        coerce=True,
        ordered=False,
    )


def validate_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Validate column presence, data types, missing values, and ranges."""
    missing_columns = sorted(set(EXPECTED_COLUMNS) - set(dataframe.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    schema = build_schema()
    validated_df = schema.validate(dataframe, lazy=True)
    return validated_df


def summarize_schema(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Return simple schema diagnostics for logging or debugging."""
    return {
        "row_count": int(len(dataframe)),
        "column_count": int(len(dataframe.columns)),
        "columns": list(dataframe.columns),
        "dtypes": {column: str(dtype) for column, dtype in dataframe.dtypes.items()},
    }

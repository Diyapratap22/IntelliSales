"""Shared helpers for IntelliSales."""

import json
from typing import Any

import numpy as np
import pandas as pd


def dataframe_to_records(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Convert a pandas DataFrame into a list of JSON-safe records.

    Handles numpy types, pandas Timestamps, and NaN values so the
    result can be serialized directly with ``json.dumps``.
    """

    records = dataframe.to_dict(orient="records")

    return [json.loads(json.dumps(record, default=_json_default)) for record in records]


def _json_default(value: Any) -> Any:
    """Convert non-JSON-serializable values into JSON-safe equivalents."""

    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating,)):
        return float(value)

    if isinstance(value, (np.bool_,)):
        return bool(value)

    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()

    if isinstance(value, (pd.Period,)):
        return str(value)

    if isinstance(value, (np.ndarray,)):
        return value.tolist()

    if pd.isna(value):
        return None

    return str(value)
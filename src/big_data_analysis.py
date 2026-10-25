"""Big data analysis for IntelliSales sales data.

Provides dataset characterization, processing-strategy recommendations,
stratified sampling for visualization, and chunked aggregation so the
dashboard remains responsive even with large sales datasets.
All computations are deterministic and use only pandas / numpy.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_ROWS_FOR_FULL_PROCESSING = 50_000
MAX_ROWS_FOR_VISUALIZATION = 10_000
CHUNK_SIZE = 10_000

MEMORY_WARNING_MB = 100
HIGH_CARDINALITY_THRESHOLD = 0.5  # fraction of unique values


# ---------------------------------------------------------------------------
# Dataset characterization
# ---------------------------------------------------------------------------

def characterize_dataset(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Return a full characterization of the dataset for big-data planning.

    Includes row/column counts, memory usage, null counts, cardinality,
    column data types, and per-column unique-value ratios.
    """

    memory_bytes = int(dataframe.memory_usage(deep=True).sum())
    memory_mb = round(memory_bytes / (1024 * 1024), 2)

    column_profiles: list[dict[str, Any]] = []
    for column in dataframe.columns:
        series = dataframe[column]
        null_count = int(series.isna().sum())
        unique_count = int(series.nunique(dropna=True))
        total_count = int(len(series))
        unique_ratio = round(unique_count / total_count, 4) if total_count > 0 else 0.0

        column_profiles.append(
            {
                "name": column,
                "dtype": str(series.dtype),
                "null_count": null_count,
                "null_pct": round((null_count / total_count) * 100, 2) if total_count > 0 else 0.0,
                "unique_count": unique_count,
                "unique_ratio": unique_ratio,
                "is_high_cardinality": unique_ratio > HIGH_CARDINALITY_THRESHOLD and total_count > 100,
            }
        )

    numeric_columns = dataframe.select_dtypes(include=[np.number]).columns.tolist()
    datetime_columns = dataframe.select_dtypes(include=["datetime64", "datetimetz"]).columns.tolist()
    categorical_columns = dataframe.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    return {
        "rows": int(len(dataframe)),
        "columns": int(len(dataframe.columns)),
        "column_names": list(dataframe.columns),
        "memory_bytes": memory_bytes,
        "memory_mb": memory_mb,
        "numeric_columns": numeric_columns,
        "datetime_columns": datetime_columns,
        "categorical_columns": categorical_columns,
        "column_profiles": column_profiles,
        "total_nulls": int(dataframe.isna().sum().sum()),
        "duplicate_rows": int(dataframe.duplicated().sum()),
    }


def get_processing_strategy(
    dataframe: pd.DataFrame,
    max_rows_for_full: int = MAX_ROWS_FOR_FULL_PROCESSING,
) -> dict[str, Any]:
    """Recommend a processing strategy based on dataset size and characteristics.

    Returns a strategy object with:
    - ``strategy``: one of ``"full"``, ``"sampled"``, ``"chunked"``
    - ``recommended_sample_rows``: target sample size if sampling is advised
    - ``warnings``: list of human-readable warnings
    - ``estimated_processing_time_seconds``: rough estimate
    """

    characterization = characterize_dataset(dataframe)
    rows = characterization["rows"]
    memory_mb = characterization["memory_mb"]
    warnings: list[str] = []

    if rows <= max_rows_for_full and memory_mb <= MEMORY_WARNING_MB:
        strategy = "full"
        sample_rows = rows
    elif rows <= max_rows_for_full and memory_mb > MEMORY_WARNING_MB:
        strategy = "chunked"
        sample_rows = rows
        warnings.append(
            f"Dataset is {memory_mb} MB — consider chunked processing for aggregations."
        )
    else:
        strategy = "sampled"
        sample_rows = min(max_rows_for_full, MAX_ROWS_FOR_VISUALIZATION)
        warnings.append(
            f"Dataset has {rows:,} rows — sampling to {sample_rows:,} rows for visualization."
        )

    high_card = [c["name"] for c in characterization["column_profiles"] if c["is_high_cardinality"]]
    if high_card:
        warnings.append(
            f"High-cardinality columns detected: {', '.join(high_card)} — "
            "grouping may produce many categories."
        )

    if characterization["total_nulls"] > 0:
        warnings.append(
            f"{characterization['total_nulls']} null values found — "
            "some aggregations may exclude nulls."
        )

    if characterization["duplicate_rows"] > 0:
        warnings.append(
            f"{characterization['duplicate_rows']} duplicate rows detected — "
            "consider deduplication before analysis."
        )

    # Rough estimate: ~1ms per 1000 rows for typical aggregations
    estimated_seconds = round(rows / 1000 * 0.001, 2)

    return {
        "strategy": strategy,
        "rows": rows,
        "recommended_sample_rows": sample_rows,
        "warnings": warnings,
        "estimated_processing_time_seconds": estimated_seconds,
        "memory_mb": memory_mb,
    }


# ---------------------------------------------------------------------------
# Sampling for visualization
# ---------------------------------------------------------------------------

def sample_for_visualization(
    dataframe: pd.DataFrame,
    max_rows: int = MAX_ROWS_FOR_VISUALIZATION,
    strategy: str = "stratified",
    group_column: str | None = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """Return a representative sample of the dataset for visualization.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Source sales dataframe.
    max_rows : int
        Maximum number of rows to return.
    strategy : str
        ``"stratified"`` (preserves group proportions) or ``"random"``.
    group_column : str | None
        Column to stratify by (e.g. ``"product"`` or ``"region"``).
        If None and strategy is ``"stratified"``, falls back to random.
    random_state : int
        Seed for reproducible sampling.

    Returns
    -------
    pd.DataFrame
        Sampled dataframe.
    """

    rows = len(dataframe)

    if rows <= max_rows:
        return dataframe.copy()

    if strategy == "stratified" and group_column and group_column in dataframe.columns:
        # Proportional stratified sampling
        group_counts = dataframe[group_column].value_counts()
        total = group_counts.sum()

        sampled_frames: list[pd.DataFrame] = []
        for group_value, count in group_counts.items():
            group_df = dataframe[dataframe[group_column] == group_value]
            group_sample_size = max(1, int(round((count / total) * max_rows)))
            group_sample_size = min(group_sample_size, len(group_df))
            sampled_frames.append(
                group_df.sample(n=group_sample_size, random_state=random_state)
            )

        result = pd.concat(sampled_frames, ignore_index=True)

        # If we overshot, trim randomly
        if len(result) > max_rows:
            result = result.sample(n=max_rows, random_state=random_state)

        return result.sort_index()

    # Random sampling fallback
    return dataframe.sample(n=max_rows, random_state=random_state)


# ---------------------------------------------------------------------------
# Chunked aggregation
# ---------------------------------------------------------------------------

def chunked_aggregate(
    dataframe: pd.DataFrame,
    group_by: str,
    agg_dict: dict[str, str | list[str]],
    chunk_size: int = CHUNK_SIZE,
) -> pd.DataFrame:
    """Aggregate a large dataframe in chunks to limit memory usage.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Source sales dataframe.
    group_by : str
        Column to group by.
    agg_dict : dict
        Column-to-aggregation mapping (pandas ``agg`` format).
    chunk_size : int
        Number of rows per chunk.

    Returns
    -------
    pd.DataFrame
        Combined aggregated results.
    """

    if len(dataframe) <= chunk_size:
        return (
            dataframe.groupby(group_by, as_index=False)
            .agg(agg_dict)
            .sort_values(by=list(agg_dict.keys())[0], ascending=False)
            .reset_index(drop=True)
        )

    chunk_results: list[pd.DataFrame] = []

    for start in range(0, len(dataframe), chunk_size):
        chunk = dataframe.iloc[start : start + chunk_size]
        chunk_agg = chunk.groupby(group_by, as_index=False).agg(agg_dict)
        chunk_results.append(chunk_agg)

    combined = pd.concat(chunk_results, ignore_index=True)

    # Re-aggregate the chunk-level results
    final_agg = {}
    for column, aggs in agg_dict.items():
        if isinstance(aggs, list):
            final_agg[column] = aggs
        else:
            final_agg[column] = [aggs]

    result = (
        combined.groupby(group_by, as_index=False)
        .agg(final_agg)
    )

    # Flatten multi-column columns if needed
    result.columns = [
        col[0] if isinstance(col, tuple) else col for col in result.columns
    ]

    # Sort by the first aggregation column descending
    sort_col = list(agg_dict.keys())[0]
    if sort_col in result.columns:
        result = result.sort_values(sort_col, ascending=False).reset_index(drop=True)

    return result


# ---------------------------------------------------------------------------
# Big data summary for dashboard
# ---------------------------------------------------------------------------

def big_data_summary(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Return a lightweight big-data summary for dashboard KPI cards.

    Combines dataset characterization with processing strategy and
    sampling recommendations.
    """

    characterization = characterize_dataset(dataframe)
    strategy = get_processing_strategy(dataframe)

    return {
        "rows": characterization["rows"],
        "columns": characterization["columns"],
        "column_names": characterization["column_names"],
        "memory_mb": characterization["memory_mb"],
        "total_nulls": characterization["total_nulls"],
        "duplicate_rows": characterization["duplicate_rows"],
        "strategy": strategy["strategy"],
        "recommended_sample_rows": strategy["recommended_sample_rows"],
        "warnings": strategy["warnings"],
        "estimated_processing_time_seconds": strategy["estimated_processing_time_seconds"],
        "numeric_columns": len(characterization["numeric_columns"]),
        "datetime_columns": len(characterization["datetime_columns"]),
        "categorical_columns": len(characterization["categorical_columns"]),
        "column_profiles": characterization["column_profiles"],
    }
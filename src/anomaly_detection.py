"""Anomaly detection for IntelliSales sales data.

Detects statistical outliers across transactions, monthly revenue trends,
and dimension-level performance (product / region / category) using
Z-score and IQR methods. All results are computed deterministically
from the uploaded dataset — no numbers are invented.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Z-score severity bands
Z_HIGH = 3.0
Z_MEDIUM = 2.5
Z_LOW = 2.0

# IQR multiplier
IQR_MULTIPLIER = 1.5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_float(value: Any) -> float | None:
    """Convert a value to float, returning None for NaN/NA so it is JSON-serialisable."""
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(result):
        return None
    return result


def _safe_int(value: Any) -> int | None:
    """Convert a value to int, returning None for NaN/NA so it is JSON-serialisable."""
    result = _safe_float(value)
    if result is None:
        return None
    return int(result)


def _severity_from_zscore(z_score: float) -> str:
    """Classify anomaly severity from the absolute Z-score."""
    abs_z = abs(z_score)
    if abs_z >= Z_HIGH:
        return "high"
    if abs_z >= Z_MEDIUM:
        return "medium"
    if abs_z >= Z_LOW:
        return "low"
    return "info"


def _severity_from_iqr(deviation: float) -> str:
    """Classify anomaly severity from an IQR-based deviation ratio."""
    if deviation >= 3.0:
        return "high"
    if deviation >= 2.0:
        return "medium"
    if deviation >= 1.5:
        return "low"
    return "info"


def _build_anomaly(
    anomaly_type: str,
    severity: str,
    z_score: float | None,
    actual_value: float | None,
    expected_value: float | None,
    description: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a standardized anomaly record."""
    actual_safe = _safe_float(actual_value)
    expected_safe = _safe_float(expected_value)

    deviation_pct = 0.0
    if expected_safe is not None and expected_safe != 0 and actual_safe is not None:
        deviation_pct = round(((actual_safe - expected_safe) / expected_safe) * 100, 2)

    record: dict[str, Any] = {
        "type": anomaly_type,
        "severity": severity,
        "z_score": round(z_score, 2) if z_score is not None else None,
        "actual_value": actual_safe,
        "expected_value": expected_safe,
        "deviation_pct": deviation_pct,
        "description": description,
    }

    if context:
        record["context"] = context

    return record


# ---------------------------------------------------------------------------
# Transaction-level anomaly detection
# ---------------------------------------------------------------------------

def detect_transaction_anomalies(
    dataframe: pd.DataFrame,
    method: str = "zscore",
    threshold: float = 2.5,
) -> list[dict[str, Any]]:
    """Flag individual sales records whose revenue deviates from the norm.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Validated sales dataframe with derived ``revenue`` column.
    method : str
        ``"zscore"`` or ``"iqr"``.
    threshold : float
        Z-score threshold (for zscore method) or IQR multiplier (for iqr).

    Returns
    -------
    list[dict]
        Anomaly records sorted by severity then absolute deviation.
    """

    required_columns = {"date", "product", "region", "category", "revenue", "profit"}
    missing = required_columns - set(dataframe.columns)
    if missing:
        raise ValueError(f"Missing columns needed for anomaly detection: {', '.join(sorted(missing))}")

    df = dataframe.copy()
    revenues = df["revenue"].astype(float)

    # Rows with NaN revenue cannot be scored and would break context values.
    valid = revenues.notna()
    if valid.sum() < 3:
        return []
    df = df.loc[valid].copy()
    revenues = revenues[valid].reset_index(drop=True)
    df = df.reset_index(drop=True)

    anomalies: list[dict[str, Any]] = []

    if method == "zscore":
        mean = float(revenues.mean())
        std = float(revenues.std())

        if std == 0:
            return []

        z_scores = (revenues - mean) / std

        for idx, z_score in z_scores.items():
            if abs(z_score) >= threshold:
                row = df.loc[idx]
                revenue = float(row["revenue"])
                severity = _severity_from_zscore(float(z_score))
                direction = "above" if z_score > 0 else "below"
                date_val = row["date"]
                date_str = (
                    pd.to_datetime(date_val).strftime("%b %d, %Y")
                    if pd.notna(date_val)
                    else "Unknown date"
                )
                anomalies.append(
                    _build_anomaly(
                        anomaly_type="transaction",
                        severity=severity,
                        z_score=float(z_score),
                        actual_value=revenue,
                        expected_value=mean,
                        description=(
                            f"{row['product']} sale in {row['region']} on "
                            f"{date_str} "
                            f"generated ₹{revenue:,.0f} revenue — "
                            f"{direction} average by {abs(float(z_score)):.1f} std devs."
                        ),
                        context={
                            "date": str(date_val) if pd.notna(date_val) else None,
                            "product": row["product"] if pd.notna(row["product"]) else None,
                            "region": row["region"] if pd.notna(row["region"]) else None,
                            "category": row["category"] if pd.notna(row["category"]) else None,
                            "quantity": _safe_int(row["quantity"]),
                            "unit_price": _safe_float(row["unit_price"]),
                            "cost": _safe_float(row["cost"]),
                            "profit": _safe_float(row["profit"]),
                        },
                    )
                )

    elif method == "iqr":
        q1 = float(revenues.quantile(0.25))
        q3 = float(revenues.quantile(0.75))
        iqr = q3 - q1

        if iqr == 0:
            return []

        lower_bound = q1 - IQR_MULTIPLIER * iqr
        upper_bound = q3 + IQR_MULTIPLIER * iqr

        for idx, row in df.iterrows():
            revenue = float(row["revenue"])
            if revenue < lower_bound or revenue > upper_bound:
                if revenue > upper_bound:
                    deviation = (revenue - q3) / iqr
                    direction = "above"
                else:
                    deviation = (q1 - revenue) / iqr
                    direction = "below"

                severity = _severity_from_iqr(deviation)
                date_val = row["date"]
                date_str = (
                    pd.to_datetime(date_val).strftime("%b %d, %Y")
                    if pd.notna(date_val)
                    else "Unknown date"
                )
                anomalies.append(
                    _build_anomaly(
                        anomaly_type="transaction",
                        severity=severity,
                        z_score=None,
                        actual_value=revenue,
                        expected_value=(q3 if revenue > upper_bound else q1),
                        description=(
                            f"{row['product']} sale in {row['region']} on "
                            f"{date_str} "
                            f"generated ₹{revenue:,.0f} revenue — "
                            f"{direction} the IQR boundary by {deviation:.1f}x IQR."
                        ),
                        context={
                            "date": str(date_val) if pd.notna(date_val) else None,
                            "product": row["product"] if pd.notna(row["product"]) else None,
                            "region": row["region"] if pd.notna(row["region"]) else None,
                            "category": row["category"] if pd.notna(row["category"]) else None,
                            "quantity": _safe_int(row["quantity"]),
                            "unit_price": _safe_float(row["unit_price"]),
                            "cost": _safe_float(row["cost"]),
                            "profit": _safe_float(row["profit"]),
                        },
                    )
                )

    anomalies.sort(key=lambda a: ({"high": 0, "medium": 1, "low": 2, "info": 3}[a["severity"]], -abs(a.get("z_score") or 0)))
    return anomalies


# ---------------------------------------------------------------------------
# Time-series anomaly detection (monthly revenue)
# ---------------------------------------------------------------------------

def detect_time_series_anomalies(
    dataframe: pd.DataFrame,
    method: str = "zscore",
    threshold: float = 2.0,
) -> list[dict[str, Any]]:
    """Flag months whose total revenue deviates from the typical monthly pattern.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Validated sales dataframe.
    method : str
        ``"zscore"`` or ``"iqr"``.
    threshold : float
        Detection threshold.

    Returns
    -------
    list[dict]
        Anomaly records for anomalous months.
    """

    required_columns = {"date", "revenue"}
    missing = required_columns - set(dataframe.columns)
    if missing:
        raise ValueError(f"Missing columns needed for time-series anomaly detection: {', '.join(sorted(missing))}")

    monthly = (
        dataframe.copy()
        .assign(month=lambda d: pd.to_datetime(d["date"]).dt.to_period("M").dt.to_timestamp())
        .groupby("month", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            _has_valid=("revenue", lambda s: s.notna().any()),
        )
    )
    # Exclude months where every revenue value was NaN.
    monthly = monthly[monthly["_has_valid"]].drop(columns=["_has_valid"])
    monthly = monthly.sort_values("month").reset_index(drop=True)

    if len(monthly) < 3:
        return []

    revenues = monthly["revenue"].astype(float)
    anomalies: list[dict[str, Any]] = []

    if method == "zscore":
        mean = float(revenues.mean())
        std = float(revenues.std())

        if std == 0:
            return []

        z_scores = (revenues - mean) / std

        for _, row in monthly.iterrows():
            idx = row.name
            z_score = float(z_scores.iloc[idx])
            if abs(z_score) >= threshold:
                severity = _severity_from_zscore(z_score)
                direction = "spike" if z_score > 0 else "drop"
                anomalies.append(
                    _build_anomaly(
                        anomaly_type="time_series",
                        severity=severity,
                        z_score=z_score,
                        actual_value=float(row["revenue"]),
                        expected_value=mean,
                        description=(
                            f"{row['month'].strftime('%b %Y')} saw a revenue {direction} "
                            f"of ₹{row['revenue']:,.0f} — {abs(z_score):.1f} std devs "
                            f"{direction} the monthly average of ₹{mean:,.0f}."
                        ),
                        context={
                            "month": row["month"].strftime("%Y-%m"),
                            "revenue": float(row["revenue"]),
                        },
                    )
                )

    elif method == "iqr":
        q1 = float(revenues.quantile(0.25))
        q3 = float(revenues.quantile(0.75))
        iqr = q3 - q1

        if iqr == 0:
            return []

        lower_bound = q1 - IQR_MULTIPLIER * iqr
        upper_bound = q3 + IQR_MULTIPLIER * iqr

        for _, row in monthly.iterrows():
            revenue = float(row["revenue"])
            if revenue < lower_bound or revenue > upper_bound:
                if revenue > upper_bound:
                    deviation = (revenue - q3) / iqr
                    direction = "spike"
                    expected = q3
                else:
                    deviation = (q1 - revenue) / iqr
                    direction = "drop"
                    expected = q1

                severity = _severity_from_iqr(deviation)
                anomalies.append(
                    _build_anomaly(
                        anomaly_type="time_series",
                        severity=severity,
                        z_score=None,
                        actual_value=revenue,
                        expected_value=expected,
                        description=(
                            f"{row['month'].strftime('%b %Y')} saw a revenue {direction} "
                            f"of ₹{revenue:,.0f} — {deviation:.1f}x IQR beyond the boundary."
                        ),
                        context={
                            "month": row["month"].strftime("%Y-%m"),
                            "revenue": revenue,
                        },
                    )
                )

    anomalies.sort(key=lambda a: ({"high": 0, "medium": 1, "low": 2, "info": 3}[a["severity"]], -abs(a.get("z_score") or 0)))
    return anomalies


# ---------------------------------------------------------------------------
# Dimension-level anomaly detection (product / region / category)
# ---------------------------------------------------------------------------

def detect_dimension_anomalies(
    dataframe: pd.DataFrame,
    group_by: str,
    metric: str = "total_revenue",
    method: str = "zscore",
    threshold: float = 2.0,
) -> list[dict[str, Any]]:
    """Flag dimension members whose aggregated metric deviates from the peer group.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Validated sales dataframe.
    group_by : str
        One of ``"product"``, ``"region"``, or ``"category"``.
    metric : str
        Aggregated metric column name (e.g. ``total_revenue``, ``total_profit``).
    method : str
        ``"zscore"`` or ``"iqr"``.
    threshold : float
        Detection threshold.

    Returns
    -------
    list[dict]
        Anomaly records for outlier dimension members.
    """

    allowed_dimensions = {"product", "region", "category"}
    if group_by not in allowed_dimensions:
        raise ValueError(f"group_by must be one of {sorted(allowed_dimensions)}")

    required_columns = {group_by, "quantity", "revenue", "profit"}
    missing = required_columns - set(dataframe.columns)
    if missing:
        raise ValueError(f"Missing columns needed for dimension anomaly detection: {', '.join(sorted(missing))}")

    summary = (
        dataframe.groupby(group_by, as_index=False)
        .agg(
            total_revenue=("revenue", "sum"),
            total_profit=("profit", "sum"),
            total_quantity=("quantity", "sum"),
            total_records=("revenue", "size"),
        )
        .sort_values("total_revenue", ascending=False)
        .reset_index(drop=True)
    )

    summary["profit_margin"] = (
        summary["total_profit"]
        .div(summary["total_revenue"].replace(0, pd.NA))
        .fillna(0)
        .mul(100)
        .round(2)
    )

    if len(summary) < 3:
        return []

    values = summary[metric].astype(float)
    anomalies: list[dict[str, Any]] = []

    if method == "zscore":
        mean = float(values.mean())
        std = float(values.std())

        if std == 0:
            return []

        z_scores = (values - mean) / std

        for _, row in summary.iterrows():
            idx = row.name
            z_score = float(z_scores.iloc[idx])
            if abs(z_score) >= threshold:
                severity = _severity_from_zscore(z_score)
                direction = "above" if z_score > 0 else "below"
                dim_value = row[group_by]
                anomalies.append(
                    _build_anomaly(
                        anomaly_type="dimension",
                        severity=severity,
                        z_score=z_score,
                        actual_value=float(row[metric]),
                        expected_value=mean,
                        description=(
                            f"{group_by.title()} '{dim_value}' {metric.replace('_', ' ')} "
                            f"is ₹{row[metric]:,.0f} — {direction} the peer average "
                            f"by {abs(z_score):.1f} std devs ({z_score:+.2f}z)."
                        ),
                        context={
                            group_by: dim_value if pd.notna(dim_value) else None,
                            "total_revenue": _safe_float(row["total_revenue"]),
                            "total_profit": _safe_float(row["total_profit"]),
                            "profit_margin": _safe_float(row["profit_margin"]),
                            "total_records": _safe_int(row["total_records"]),
                        },
                    )
                )

    anomalies.sort(key=lambda a: ({"high": 0, "medium": 1, "low": 2, "info": 3}[a["severity"]], -abs(a.get("z_score") or 0)))
    return anomalies


def _detect_dimension_anomalies_iqr(
    dataframe: pd.DataFrame,
    group_by: str,
    metric: str,
    threshold: float,
) -> list[dict[str, Any]]:
    """IQR-based dimension anomaly detection (internal helper)."""

    summary = (
        dataframe.groupby(group_by, as_index=False)
        .agg(
            total_revenue=("revenue", "sum"),
            total_profit=("profit", "sum"),
            total_quantity=("quantity", "sum"),
            total_records=("revenue", "size"),
        )
        .sort_values("total_revenue", ascending=False)
        .reset_index(drop=True)
    )

    summary["profit_margin"] = (
        summary["total_profit"]
        .div(summary["total_revenue"].replace(0, pd.NA))
        .fillna(0)
        .mul(100)
        .round(2)
    )

    values = summary[metric].astype(float)
    q1 = float(values.quantile(0.25))
    q3 = float(values.quantile(0.75))
    iqr = q3 - q1

    if iqr == 0:
        return []

    lower_bound = q1 - IQR_MULTIPLIER * iqr
    upper_bound = q3 + IQR_MULTIPLIER * iqr
    anomalies: list[dict[str, Any]] = []

    for _, row in summary.iterrows():
        value = float(row[metric])
        if value < lower_bound or value > upper_bound:
            if value > upper_bound:
                deviation = (value - q3) / iqr
                direction = "above"
                expected = q3
            else:
                deviation = (q1 - value) / iqr
                direction = "below"
                expected = q1

            severity = _severity_from_iqr(deviation)
            dim_value = row[group_by]
            anomalies.append(
                _build_anomaly(
                    anomaly_type="dimension",
                    severity=severity,
                    z_score=None,
                    actual_value=value,
                    expected_value=expected,
                    description=(
                        f"{group_by.title()} '{dim_value}' {metric.replace('_', ' ')} "
                        f"is ₹{value:,.0f} — {direction} the peer IQR boundary "
                        f"by {deviation:.1f}x IQR."
                    ),
                    context={
                        group_by: dim_value if pd.notna(dim_value) else None,
                        "total_revenue": _safe_float(row["total_revenue"]),
                        "total_profit": _safe_float(row["total_profit"]),
                        "profit_margin": _safe_float(row["profit_margin"]),
                        "total_records": _safe_int(row["total_records"]),
                    },
                )
            )

    anomalies.sort(key=lambda a: ({"high": 0, "medium": 1, "low": 2, "info": 3}[a["severity"]], -abs(a.get("z_score") or 0)))
    return anomalies


# ---------------------------------------------------------------------------
# Combined analysis
# ---------------------------------------------------------------------------

def run_full_anomaly_analysis(
    dataframe: pd.DataFrame,
    threshold: float = 2.5,
) -> dict[str, Any]:
    """Run all anomaly detection methods and return combined results.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Validated sales dataframe.
    threshold : float
        Z-score threshold for flagging anomalies.

    Returns
    -------
    dict
        {
            "transactions": [...],
            "time_series": [...],
            "dimensions": {
                "product": [...],
                "region": [...],
                "category": [...],
            },
            "summary": { ... }
        }
    """

    transactions = detect_transaction_anomalies(dataframe, method="zscore", threshold=threshold)
    # Time series uses its own default threshold (2.0) because monthly aggregates
    # have fewer data points and need a more sensitive threshold than transactions.
    time_series = detect_time_series_anomalies(dataframe, method="zscore")
    product_anomalies = detect_dimension_anomalies(dataframe, "product", method="zscore", threshold=threshold)
    region_anomalies = detect_dimension_anomalies(dataframe, "region", method="zscore", threshold=threshold)
    category_anomalies = detect_dimension_anomalies(dataframe, "category", method="zscore", threshold=threshold)

    all_anomalies = transactions + time_series + product_anomalies + region_anomalies + category_anomalies

    severity_counts = {"high": 0, "medium": 0, "low": 0, "info": 0}
    for anomaly in all_anomalies:
        severity_counts[anomaly["severity"]] = severity_counts.get(anomaly["severity"], 0) + 1

    return {
        "transactions": transactions,
        "time_series": time_series,
        "dimensions": {
            "product": product_anomalies,
            "region": region_anomalies,
            "category": category_anomalies,
        },
        "summary": {
            "total_anomalies": len(all_anomalies),
            "high_severity": severity_counts["high"],
            "medium_severity": severity_counts["medium"],
            "low_severity": severity_counts["low"],
            "info_severity": severity_counts["info"],
            "transaction_anomalies": len(transactions),
            "time_series_anomalies": len(time_series),
            "dimension_anomalies": len(product_anomalies) + len(region_anomalies) + len(category_anomalies),
        },
    }


def get_anomaly_summary(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Return a lightweight anomaly summary for dashboard KPI cards."""
    analysis = run_full_anomaly_analysis(dataframe)
    return analysis["summary"]
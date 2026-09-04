import numpy as np
import pandas as pd


def get_monthly_revenue(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate transaction-level sales data into monthly revenue totals.
    """

    required_columns = {"date", "revenue"}
    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing columns needed for forecasting: {missing}")

    monthly_data = dataframe.copy()
    monthly_data["month"] = (
        pd.to_datetime(monthly_data["date"])
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly_revenue = (
        monthly_data.groupby("month", as_index=False)["revenue"]
        .sum()
        .sort_values("month")
        .reset_index(drop=True)
    )

    return monthly_revenue


def forecast_monthly_revenue(
    dataframe: pd.DataFrame,
    periods: int = 3,
) -> pd.DataFrame:
    """
    Forecast future monthly revenue using a linear trend model.

    Returns a DataFrame with columns:
        month, forecast_revenue, lower_bound, upper_bound
    """

    if periods <= 0:
        raise ValueError("Forecast periods must be greater than zero.")

    monthly_revenue = get_monthly_revenue(dataframe)

    if len(monthly_revenue) < 3:
        raise ValueError(
            "At least three months of sales data are needed for forecasting."
        )

    time_index = np.arange(len(monthly_revenue))

    slope, intercept = np.polyfit(
        time_index,
        monthly_revenue["revenue"],
        1,
    )

    future_index = np.arange(
        len(monthly_revenue),
        len(monthly_revenue) + periods,
    )

    future_revenue = np.maximum(
        0,
        slope * future_index + intercept,
    )

    residuals = monthly_revenue["revenue"] - (
        slope * time_index + intercept
    )
    residual_std = float(residuals.std())

    next_month = monthly_revenue["month"].iloc[-1] + pd.offsets.MonthBegin(1)

    future_months = pd.date_range(
        start=next_month,
        periods=periods,
        freq="MS",
    )

    return pd.DataFrame(
        {
            "month": future_months,
            "forecast_revenue": future_revenue.round(2),
            "lower_bound": np.maximum(0, future_revenue - 1.96 * residual_std).round(2),
            "upper_bound": (future_revenue + 1.96 * residual_std).round(2),
        }
    )


def get_forecast_series(
    dataframe: pd.DataFrame,
    periods: int = 3,
) -> dict[str, list[dict]]:
    """
    Build a combined historical + forecast series for charting.

    Returns:
        {
            "historical": [{"month": ..., "revenue": ...}, ...],
            "forecast": [{"month": ..., "forecast_revenue": ..., "lower_bound": ..., "upper_bound": ...}, ...]
        }
    """

    historical = get_monthly_revenue(dataframe)
    forecast = forecast_monthly_revenue(dataframe, periods=periods)

    historical_records = [
        {
            "month": row["month"].strftime("%Y-%m"),
            "revenue": float(row["revenue"]),
        }
        for _, row in historical.iterrows()
    ]

    forecast_records = [
        {
            "month": row["month"].strftime("%Y-%m"),
            "forecast_revenue": float(row["forecast_revenue"]),
            "lower_bound": float(row["lower_bound"]),
            "upper_bound": float(row["upper_bound"]),
        }
        for _, row in forecast.iterrows()
    ]

    return {
        "historical": historical_records,
        "forecast": forecast_records,
    }
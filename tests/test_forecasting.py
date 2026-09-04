from pathlib import Path

import pandas as pd

from src.data_loader import load_sales_data
from src.forecasting import (
    forecast_monthly_revenue,
    get_forecast_series,
    get_monthly_revenue,
)


def _load_sample() -> pd.DataFrame:
    """Load the sample sales data for tests."""

    project_root = Path(__file__).resolve().parents[1]
    sample_file = project_root / "data" / "raw" / "sample_sales.csv"

    return load_sales_data(sample_file)


def test_get_monthly_revenue_returns_monthly_totals():
    """Monthly revenue is aggregated correctly from transactions."""

    dataframe = _load_sample()
    monthly = get_monthly_revenue(dataframe)

    assert len(monthly) == 24
    assert "month" in monthly.columns
    assert "revenue" in monthly.columns
    assert monthly["revenue"].iloc[0] == 660000.0


def test_forecast_monthly_revenue_returns_forecast_with_confidence():
    """Forecast returns the requested number of periods with bounds."""

    dataframe = _load_sample()
    forecast = forecast_monthly_revenue(dataframe, periods=3)

    assert len(forecast) == 3
    assert "month" in forecast.columns
    assert "forecast_revenue" in forecast.columns
    assert "lower_bound" in forecast.columns
    assert "upper_bound" in forecast.columns
    assert (forecast["lower_bound"] <= forecast["forecast_revenue"]).all()
    assert (forecast["upper_bound"] >= forecast["forecast_revenue"]).all()


def test_forecast_monthly_revenue_requires_positive_periods():
    """Forecast periods must be greater than zero."""

    dataframe = _load_sample()

    try:
        forecast_monthly_revenue(dataframe, periods=0)
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "greater than zero" in str(error)


def test_get_forecast_series_returns_historical_and_forecast():
    """The combined series has historical and forecast records."""

    dataframe = _load_sample()
    series = get_forecast_series(dataframe, periods=6)

    assert "historical" in series
    assert "forecast" in series
    assert len(series["historical"]) == 24
    assert len(series["forecast"]) == 6
    assert "month" in series["historical"][0]
    assert "revenue" in series["historical"][0]
    assert "forecast_revenue" in series["forecast"][0]
    assert "lower_bound" in series["forecast"][0]
    assert "upper_bound" in series["forecast"][0]
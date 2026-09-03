from pathlib import Path

from src.analytics import (
    calculate_sales_summary,
    summarize_performance_by,
)
from src.data_loader import load_sales_data

def test_calculate_sales_summary_returns_correct_metrics():
    """The sample data produces the expected business KPIs."""

    project_root = Path(__file__).resolve().parents[1]

    sample_file = (
        project_root
        / "data"
        / "raw"
        / "sample_sales.csv"
    )

    dataframe = load_sales_data(sample_file)
    summary = calculate_sales_summary(dataframe)

    assert summary["total_revenue"] == 21576000.0
    assert summary["total_profit"] == 5066000.0
    assert summary["total_quantity"] == 649
    assert summary["total_transactions"] == 24
    assert summary["profit_margin"] == 23.48

def test_summarize_performance_by_product_and_region():
    """Product and region performance is calculated and ranked correctly."""

    project_root = Path(__file__).resolve().parents[1]

    sample_file = (
        project_root
        / "data"
        / "raw"
        / "sample_sales.csv"
    )

    dataframe = load_sales_data(sample_file)

    product_summary = summarize_performance_by(dataframe, "product")

    assert list(product_summary["product"]) == ["Laptop", "Phone", "Tablet"]
    assert product_summary.iloc[0]["total_revenue"] == 8470000
    assert product_summary.iloc[0]["total_profit"] == 2300000

    region_summary = summarize_performance_by(dataframe, "region")

    assert region_summary.iloc[0]["region"] == "East"
    assert region_summary.iloc[0]["total_revenue"] == 5577000
    assert region_summary.iloc[0]["total_profit"] == 1337000
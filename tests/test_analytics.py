from pathlib import Path

from src.analytics import calculate_sales_summary
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
from pathlib import Path

from src.data_loader import load_sales_data


def test_load_sales_data_calculates_business_metrics():
    """The sample sales file loads and receives correct derived metrics."""

    project_root = Path(__file__).resolve().parents[1]

    sample_file = (
        project_root
        / "data"
        / "raw"
        / "sample_sales.csv"
    )

    dataframe = load_sales_data(sample_file)

    assert len(dataframe) == 24
    assert "revenue" in dataframe.columns
    assert "profit" in dataframe.columns

    first_sale = dataframe.iloc[0]

    assert first_sale["revenue"] == 660000
    assert first_sale["profit"] == 180000
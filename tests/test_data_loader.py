from io import BytesIO
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

def test_load_sales_data_accepts_uploaded_csv():
    """An uploaded CSV-like file is loaded and analyzed correctly."""

    uploaded_file = BytesIO(
        b"date,product,region,quantity,unit_price,cost\n"
        b"2026-01-01,Monitor,North,2,15000,20000\n"
    )

    uploaded_file.name = "uploaded_sales.csv"

    dataframe = load_sales_data(uploaded_file)

    assert len(dataframe) == 1
    assert dataframe.iloc[0]["revenue"] == 30000
    assert dataframe.iloc[0]["profit"] == 10000
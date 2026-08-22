import pandas as pd

from src.data_profiler import profile_data


def test_profile_data():
    """Test that IntelliSales can generate a profile report."""

    data = {
        "Product": ["Laptop", "Phone", "Tablet"],
        "Region": ["North", "South", "East"],
        "Sales": [50000, 30000, 20000],
        "Quantity": [5, 3, 2]
    }

    df = pd.DataFrame(data)

    profile = profile_data(df)

    assert profile is not None
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "date",
    "product",
    "region",
    "quantity",
    "unit_price",
    "cost",
}


def load_sales_data(file_path: str | Path) -> pd.DataFrame:
    """
    Load a CSV or Excel sales file, validate its core fields,
    and calculate reliable business metrics.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Sales file not found: {path}")

    if path.suffix.lower() == ".csv":
        dataframe = pd.read_csv(path)
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        dataframe = pd.read_excel(path)
    else:
        raise ValueError("Only CSV and Excel files are supported.")

    dataframe.columns = (
        dataframe.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    dataframe["date"] = pd.to_datetime(dataframe["date"], errors="coerce")

    numeric_columns = ["quantity", "unit_price", "cost"]

    for column in numeric_columns:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

    if dataframe["date"].isna().any():
        raise ValueError("The 'date' column contains invalid or missing dates.")

    if (
        dataframe[["product", "region"]].isna().any().any()
        or dataframe["product"].astype("string").str.strip().eq("").any()
        or dataframe["region"].astype("string").str.strip().eq("").any()
    ):
        raise ValueError("The 'product' and 'region' columns must not be blank.")

    if dataframe[numeric_columns].isna().any().any():
        raise ValueError(
            "The 'quantity', 'unit_price', and 'cost' columns must contain valid numbers."
        )

    if (dataframe["quantity"] <= 0).any():
        raise ValueError(
            "The 'quantity' column must contain values greater than zero."
        )

    if (dataframe["quantity"] % 1 != 0).any():
        raise ValueError("The 'quantity' column must contain whole numbers.")

    if (dataframe[["unit_price", "cost"]] < 0).any().any():
        raise ValueError(
            "The 'unit_price' and 'cost' columns cannot contain negative values."
        )

    dataframe["revenue"] = dataframe["quantity"] * dataframe["unit_price"]
    dataframe["profit"] = dataframe["revenue"] - dataframe["cost"]

    return dataframe
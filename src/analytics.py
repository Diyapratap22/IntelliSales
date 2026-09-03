import pandas as pd


def calculate_sales_summary(dataframe: pd.DataFrame) -> dict[str, float | int]:
    """
    Calculate headline sales metrics from validated sales data.
    """

    required_columns = {"date", "quantity", "revenue", "profit"}
    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing columns needed for analysis: {missing}")

    total_revenue = float(dataframe["revenue"].sum())
    total_profit = float(dataframe["profit"].sum())
    total_quantity = int(dataframe["quantity"].sum())
    total_transactions = int(len(dataframe))

    profit_margin = 0.0

    if total_revenue != 0:
        profit_margin = round((total_profit / total_revenue) * 100, 2)

    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_quantity": total_quantity,
        "total_transactions": total_transactions,
        "profit_margin": profit_margin,
    }
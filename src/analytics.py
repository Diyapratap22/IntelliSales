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

def summarize_performance_by(
    dataframe: pd.DataFrame,
    group_by: str,
) -> pd.DataFrame:
    """
    Summarize revenue, profit, and units sold by product or region.
    """

    allowed_dimensions = {"product", "region"}

    if group_by not in allowed_dimensions:
        raise ValueError(
            "Analysis is only available by 'product' or 'region'."
        )

    required_columns = {
        group_by,
        "quantity",
        "revenue",
        "profit",
    }

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing columns needed for analysis: {missing}")

    summary = (
        dataframe.groupby(group_by, as_index=False)
        .agg(
            total_revenue=("revenue", "sum"),
            total_profit=("profit", "sum"),
            total_quantity=("quantity", "sum"),
            total_transactions=("revenue", "size"),
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

    return summary
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
    total_records = int(len(dataframe))

    profit_margin = 0.0

    if total_revenue != 0:
        profit_margin = round((total_profit / total_revenue) * 100, 2)

    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_quantity": total_quantity,
        "total_records": total_records,
        "total_transactions": total_records,
        "profit_margin": profit_margin,
    }


def summarize_performance_by(
    dataframe: pd.DataFrame,
    group_by: str,
) -> pd.DataFrame:
    """
    Summarize revenue, profit, and units sold by product, region, or category.
    """

    allowed_dimensions = {"product", "region", "category"}

    if group_by not in allowed_dimensions:
        raise ValueError(
            "Analysis is only available by 'product', 'region', or 'category'."
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
            total_records=("revenue", "size"),
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


def get_revenue_trend(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate transaction-level sales data into a monthly revenue trend.
    """

    required_columns = {"date", "revenue"}
    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing columns needed for trend analysis: {missing}")

    trend_data = dataframe.copy()
    trend_data["month"] = (
        pd.to_datetime(trend_data["date"])
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly_trend = (
        trend_data.groupby("month", as_index=False)["revenue"]
        .sum()
        .sort_values("month")
        .reset_index(drop=True)
    )

    return monthly_trend


def _compute_dimension_growth(
    dataframe: pd.DataFrame,
    group_by: str,
) -> pd.Series:
    """
    Compute revenue growth (%) between the first and second half of the period
    for a given dimension (product, region, or category).
    """

    df = dataframe.copy()
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()

    midpoint = df["month"].median()

    first_half = (
        df[df["month"] <= midpoint]
        .groupby(group_by)["revenue"]
        .sum()
    )
    second_half = (
        df[df["month"] > midpoint]
        .groupby(group_by)["revenue"]
        .sum()
    )

    growth = (
        (second_half - first_half)
        .div(first_half.replace(0, pd.NA))
        .mul(100)
        .dropna()
        .sort_values(ascending=False)
    )

    return growth


def generate_verified_insights(dataframe: pd.DataFrame) -> list[dict[str, str]]:
    """
    Generate rule-based insights from verified calculations.

    Every insight is derived directly from the dataset using the
    deterministic analytics functions above. No numbers are invented.
    """

    summary = calculate_sales_summary(dataframe)
    product_summary = summarize_performance_by(dataframe, "product")
    region_summary = summarize_performance_by(dataframe, "region")
    category_summary = summarize_performance_by(dataframe, "category")
    trend = get_revenue_trend(dataframe)

    insights: list[dict[str, str]] = []

    top_product = product_summary.iloc[0]
    insights.append(
        {
            "type": "top_product",
            "title": "Strongest Product",
            "message": (
                f"{top_product['product']} leads revenue at "
                f"₹{top_product['total_revenue']:,.0f} "
                f"({top_product['profit_margin']:.1f}% margin)."
            ),
        }
    )

    top_region = region_summary.iloc[0]
    insights.append(
        {
            "type": "top_region",
            "title": "Strongest Region",
            "message": (
                f"{top_region['region']} is the strongest region with "
                f"₹{top_region['total_revenue']:,.0f} in revenue."
            ),
        }
    )

    top_category = category_summary.iloc[0]
    insights.append(
        {
            "type": "top_category",
            "title": "Leading Category",
            "message": (
                f"{top_category['category']} is the leading category with "
                f"₹{top_category['total_revenue']:,.0f} in revenue."
            ),
        }
    )

    if len(product_summary) > 1 and summary["total_revenue"] > 0:
        top_share = (top_product["total_revenue"] / summary["total_revenue"]) * 100
        insights.append(
            {
                "type": "driver",
                "title": "Key Revenue Driver",
                "message": (
                    f"{top_product['product']} drives {top_share:.1f}% of total revenue."
                ),
            }
        )

    if len(trend) >= 2:
        first_month = trend.iloc[0]
        last_month = trend.iloc[-1]

        if first_month["revenue"] > 0:
            growth = (
                (last_month["revenue"] - first_month["revenue"])
                / first_month["revenue"]
            ) * 100
            direction = "up" if growth >= 0 else "down"
            insights.append(
                {
                    "type": "trend",
                    "title": "Revenue Trend",
                    "message": (
                        f"Revenue has trended {direction} "
                        f"{abs(growth):.1f}% from "
                        f"{first_month['month'].strftime('%b %Y')} to "
                        f"{last_month['month'].strftime('%b %Y')}."
                    ),
                }
            )

    if len(product_summary) > 1:
        growth = _compute_dimension_growth(dataframe, "product")
        if len(growth) > 0:
            fastest = growth.index[0]
            fastest_growth = growth.iloc[0]
            insights.append(
                {
                    "type": "opportunity",
                    "title": "Top Opportunity",
                    "message": (
                        f"{fastest} is the fastest-growing product at "
                        f"{fastest_growth:+.1f}% revenue growth "
                        f"(first half vs second half)."
                    ),
                }
            )

    if len(trend) >= 3:
        best_month = trend.loc[trend["revenue"].idxmax()]
        insights.append(
            {
                "type": "anomaly",
                "title": "Peak Month",
                "message": (
                    f"{best_month['month'].strftime('%b %Y')} was the peak "
                    f"revenue month at ₹{best_month['revenue']:,.0f}."
                ),
            }
        )

    if summary["profit_margin"] > 0:
        insights.append(
            {
                "type": "profitability",
                "title": "Profitability",
                "message": (
                    f"Overall profit margin is {summary['profit_margin']:.1f}% "
                    f"on ₹{summary['total_revenue']:,.0f} revenue."
                ),
            }
        )

    return insights
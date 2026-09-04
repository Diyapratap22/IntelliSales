"""IntelliSales AI Analyst.

The analyst interprets a natural-language question, selects a deterministic
analytics tool, executes it against the real dataset, and formats the
verified result. It never invents business numbers.
"""

from __future__ import annotations

from typing import Any, Callable

import pandas as pd

from src.analytics import (
    calculate_sales_summary,
    generate_verified_insights,
    get_revenue_trend,
    summarize_performance_by,
)
from src.forecasting import forecast_monthly_revenue


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

ToolFunction = Callable[[pd.DataFrame, str], dict[str, Any]]


def _tool_summary(dataframe: pd.DataFrame, question: str) -> dict[str, Any]:
    """Return headline KPI metrics."""

    summary = calculate_sales_summary(dataframe)

    return {
        "tool": "sales_summary",
        "answer": (
            f"Total revenue is ₹{summary['total_revenue']:,.0f} across "
            f"{summary['total_records']} records, with "
            f"₹{summary['total_profit']:,.0f} profit "
            f"({summary['profit_margin']:.1f}% margin) and "
            f"{summary['total_quantity']:,} units sold."
        ),
        "data": summary,
    }


def _tool_top_product(dataframe: pd.DataFrame, question: str) -> dict[str, Any]:
    """Return the highest-revenue product."""

    summary = summarize_performance_by(dataframe, "product")
    top = summary.iloc[0]

    return {
        "tool": "top_product",
        "answer": (
            f"{top['product']} is the top product with "
            f"₹{top['total_revenue']:,.0f} revenue and "
            f"{top['profit_margin']:.1f}% margin."
        ),
        "data": top.to_dict(),
    }


def _tool_top_region(dataframe: pd.DataFrame, question: str) -> dict[str, Any]:
    """Return the highest-revenue region."""

    summary = summarize_performance_by(dataframe, "region")
    top = summary.iloc[0]

    return {
        "tool": "top_region",
        "answer": (
            f"{top['region']} is the top region with "
            f"₹{top['total_revenue']:,.0f} revenue and "
            f"{top['profit_margin']:.1f}% margin."
        ),
        "data": top.to_dict(),
    }


def _tool_top_profit_region(dataframe: pd.DataFrame, question: str) -> dict[str, Any]:
    """Return the region with the highest profit."""

    summary = summarize_performance_by(dataframe, "region")
    top = summary.sort_values("total_profit", ascending=False).iloc[0]

    return {
        "tool": "top_profit_region",
        "answer": (
            f"{top['region']} generated the most profit at "
            f"₹{top['total_profit']:,.0f} with a "
            f"{top['profit_margin']:.1f}% margin."
        ),
        "data": top.to_dict(),
    }


def _tool_top_category(dataframe: pd.DataFrame, question: str) -> dict[str, Any]:
    """Return the highest-revenue category."""

    summary = summarize_performance_by(dataframe, "category")
    top = summary.iloc[0]

    return {
        "tool": "top_category",
        "answer": (
            f"{top['category']} is the top category with "
            f"₹{top['total_revenue']:,.0f} revenue and "
            f"{top['profit_margin']:.1f}% margin."
        ),
        "data": top.to_dict(),
    }


def _tool_forecast(dataframe: pd.DataFrame, question: str) -> dict[str, Any]:
    """Return the next-month revenue forecast."""

    try:
        forecast = forecast_monthly_revenue(dataframe, periods=1)
    except ValueError as error:
        return {
            "tool": "forecast",
            "answer": f"Forecasting is not available: {error}",
            "data": {},
        }

    row = forecast.iloc[0]
    month_label = row["month"].strftime("%B %Y")

    return {
        "tool": "forecast",
        "answer": (
            f"Projected revenue for {month_label} is "
            f"₹{row['forecast_revenue']:,.0f} "
            f"(range ₹{row['lower_bound']:,.0f} – ₹{row['upper_bound']:,.0f})."
        ),
        "data": forecast.to_dict(orient="records")[0],
    }


def _tool_trend(dataframe: pd.DataFrame, question: str) -> dict[str, Any]:
    """Return the monthly revenue trend summary."""

    trend = get_revenue_trend(dataframe)

    if len(trend) < 2:
        return {
            "tool": "trend",
            "answer": "Not enough data to describe a revenue trend.",
            "data": {},
        }

    first = trend.iloc[0]
    last = trend.iloc[-1]
    growth = ((last["revenue"] - first["revenue"]) / first["revenue"]) * 100
    direction = "up" if growth >= 0 else "down"

    return {
        "tool": "trend",
        "answer": (
            f"Monthly revenue trended {direction} {abs(growth):.1f}% from "
            f"{first['month'].strftime('%b %Y')} (₹{first['revenue']:,.0f}) to "
            f"{last['month'].strftime('%b %Y')} (₹{last['revenue']:,.0f})."
        ),
        "data": {
            "first_month": first["month"].isoformat(),
            "last_month": last["month"].isoformat(),
            "first_revenue": float(first["revenue"]),
            "last_revenue": float(last["revenue"]),
            "growth_pct": round(growth, 2),
        },
    }


def _tool_revenue_change(dataframe: pd.DataFrame, question: str) -> dict[str, Any]:
    """Explain why revenue changed between the first and second half."""

    trend = get_revenue_trend(dataframe)

    if len(trend) < 2:
        return {
            "tool": "revenue_change",
            "answer": "Not enough data to explain revenue changes.",
            "data": {},
        }

    midpoint = len(trend) // 2
    first_half = trend.iloc[:midpoint]
    second_half = trend.iloc[midpoint:]

    first_total = float(first_half["revenue"].sum())
    second_total = float(second_half["revenue"].sum())
    change = second_total - first_total
    change_pct = (change / first_total * 100) if first_total else 0.0

    product_summary = summarize_performance_by(dataframe, "product")
    product_growth = {}
    for _, row in product_summary.iterrows():
        product_data = dataframe[dataframe["product"] == row["product"]]
        product_trend = get_revenue_trend(product_data)
        if len(product_trend) >= 2:
            p_mid = len(product_trend) // 2
            p_first = float(product_trend.iloc[:p_mid]["revenue"].sum())
            p_second = float(product_trend.iloc[p_mid:]["revenue"].sum())
            if p_first > 0:
                product_growth[row["product"]] = (p_second - p_first) / p_first * 100

    if product_growth:
        top_gainer = max(product_growth, key=product_growth.get)
        top_loser = min(product_growth, key=product_growth.get)
        explanation = (
            f"Revenue {'increased' if change >= 0 else 'decreased'} by "
            f"₹{abs(change):,.0f} ({change_pct:+.1f}%) from the first half "
            f"to the second half of the period. "
            f"{top_gainer} grew the most at {product_growth[top_gainer]:+.1f}%, "
            f"while {top_loser} changed by {product_growth[top_loser]:+.1f}%."
        )
    else:
        explanation = (
            f"Revenue {'increased' if change >= 0 else 'decreased'} by "
            f"₹{abs(change):,.0f} ({change_pct:+.1f}%) from the first half "
            f"to the second half of the period."
        )

    return {
        "tool": "revenue_change",
        "answer": explanation,
        "data": {
            "first_half_revenue": round(first_total, 2),
            "second_half_revenue": round(second_total, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "product_growth": {k: round(v, 2) for k, v in product_growth.items()},
        },
    }


def _tool_recommendations(dataframe: pd.DataFrame, question: str) -> dict[str, Any]:
    """Return data-driven recommendations based on verified metrics."""

    summary = calculate_sales_summary(dataframe)
    product_summary = summarize_performance_by(dataframe, "product")
    region_summary = summarize_performance_by(dataframe, "region")
    trend = get_revenue_trend(dataframe)

    recommendations: list[str] = []

    top_product = product_summary.iloc[0]
    recommendations.append(
        f"Focus on {top_product['product']} — it is your top revenue product "
        f"at ₹{top_product['total_revenue']:,.0f}."
    )

    if len(product_summary) > 1:
        lowest = product_summary.iloc[-1]
        recommendations.append(
            f"Review {lowest['product']} — it has the lowest revenue at "
            f"₹{lowest['total_revenue']:,.0f}."
        )

    top_region = region_summary.iloc[0]
    recommendations.append(
        f"Expand in {top_region['region']} — it leads with "
        f"₹{top_region['total_revenue']:,.0f} in revenue."
    )

    if len(trend) >= 2:
        last = trend.iloc[-1]
        prev = trend.iloc[-2]
        if last["revenue"] > prev["revenue"]:
            recommendations.append(
                f"Revenue momentum is positive — the latest month "
                f"(₹{last['revenue']:,.0f}) is above the previous month."
            )
        else:
            recommendations.append(
                f"Revenue dipped in the latest month "
                f"(₹{last['revenue']:,.0f} vs ₹{prev['revenue']:,.0f} previously) — "
                f"investigate the cause."
            )

    return {
        "tool": "recommendations",
        "answer": "Here are data-driven recommendations based on your verified metrics:",
        "data": recommendations,
    }


def _tool_insights(dataframe: pd.DataFrame, question: str) -> dict[str, Any]:
    """Return all verified insights."""

    insights = generate_verified_insights(dataframe)

    return {
        "tool": "insights",
        "answer": "Here are the verified insights from your data:",
        "data": insights,
    }


TOOLS: list[tuple[str, list[str], ToolFunction]] = [
    (
        "sales_summary",
        ["summary", "kpi", "overview", "total revenue", "total profit", "margin", "units", "revenue"],
        _tool_summary,
    ),
    (
        "top_product",
        ["top product", "best product", "highest product", "product performance", "which product"],
        _tool_top_product,
    ),
    (
        "top_region",
        ["top region", "best region", "highest region", "regional performance", "which region"],
        _tool_top_region,
    ),
    (
        "top_profit_region",
        ["most profit", "highest profit", "profit by region", "profitable region"],
        _tool_top_profit_region,
    ),
    (
        "top_category",
        ["top category", "best category", "highest category", "category performance"],
        _tool_top_category,
    ),
    (
        "forecast",
        ["forecast", "predict", "projection", "future", "next month", "expected revenue"],
        _tool_forecast,
    ),
    (
        "trend",
        ["trend", "growth", "over time", "monthly", "increase", "decrease"],
        _tool_trend,
    ),
    (
        "revenue_change",
        ["why did revenue", "why revenue", "revenue change", "what changed", "explain the change"],
        _tool_revenue_change,
    ),
    (
        "recommendations",
        ["focus on", "recommend", "what should i", "action", "improve", "priority"],
        _tool_recommendations,
    ),
    (
        "insights",
        ["insight", "driver", "analysis", "what is happening", "explain"],
        _tool_insights,
    ),
]


def _classify_intent(question: str) -> str | None:
    """Match a question to a tool name using keyword patterns."""

    normalized = question.lower()

    for tool_name, keywords, _ in TOOLS:
        for keyword in keywords:
            if keyword in normalized:
                return tool_name

    return None


def answer_question(question: str, dataframe: pd.DataFrame) -> dict[str, Any]:
    """
    Answer a natural-language question using verified analytics tools.

    The question is classified to a deterministic tool, which computes
    the answer from the real dataset. No numbers are invented.
    """

    tool_name = _classify_intent(question)

    if tool_name is None:
        supported = ", ".join(
            [
                "sales summary",
                "top product",
                "top region",
                "top category",
                "forecast",
                "revenue trend",
                "revenue change",
                "recommendations",
                "insights",
            ]
        )

        return {
            "question": question,
            "tool": None,
            "answer": (
                "I can only answer questions backed by verified calculations. "
                f"Try asking about: {supported}."
            ),
            "data": {},
        }

    for name, _, function in TOOLS:
        if name == tool_name:
            result = function(dataframe, question)
            result["question"] = question
            return result

    return {
        "question": question,
        "tool": None,
        "answer": "I could not process that question.",
        "data": {},
    }
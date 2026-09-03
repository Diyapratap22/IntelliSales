from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analytics import calculate_sales_summary, summarize_performance_by
from src.data_loader import load_sales_data


SAMPLE_FILE = PROJECT_ROOT / "data" / "raw" / "sample_sales.csv"


@st.cache_data
def load_dashboard_data():
    """Load the included sample data once and reuse it efficiently."""

    return load_sales_data(SAMPLE_FILE)


def format_currency(value: float) -> str:
    """Format a number as Indian currency for dashboard display."""

    return f"₹{value:,.0f}"


st.set_page_config(
    page_title="IntelliSales",
    page_icon="📊",
    layout="wide",
)

st.title("📊 IntelliSales")
st.caption("AI Data Analyst for Sales Intelligence & Forecasting")

st.sidebar.header("Dashboard")
st.sidebar.success("Sample sales data loaded")
st.sidebar.caption(
    "This first dashboard uses validated data and verified analytics."
)

dataframe = load_dashboard_data()
summary = calculate_sales_summary(dataframe)
product_summary = summarize_performance_by(dataframe, "product")
region_summary = summarize_performance_by(dataframe, "region")

st.subheader("Business Overview")

revenue_column, profit_column, quantity_column, margin_column = st.columns(4)

revenue_column.metric("Total Revenue", format_currency(summary["total_revenue"]))
profit_column.metric("Total Profit", format_currency(summary["total_profit"]))
quantity_column.metric("Units Sold", f"{summary['total_quantity']:,}")
margin_column.metric("Profit Margin", f"{summary['profit_margin']}%")

st.divider()

left_column, right_column = st.columns(2)

with left_column:
    st.subheader("Revenue by Product")
    st.bar_chart(product_summary.set_index("product")["total_revenue"])

with right_column:
    st.subheader("Revenue by Region")
    st.bar_chart(region_summary.set_index("region")["total_revenue"])

top_product = product_summary.iloc[0]
top_region = region_summary.iloc[0]

st.subheader("Verified Insights")
st.write(
    f"• **{top_product['product']}** is the highest-revenue product, "
    f"generating {format_currency(top_product['total_revenue'])}."
)
st.write(
    f"• **{top_region['region']}** is the highest-revenue region, "
    f"generating {format_currency(top_region['total_revenue'])}."
)

st.subheader("Performance Details")
st.dataframe(
    region_summary,
    hide_index=True,
    use_container_width=True,
)
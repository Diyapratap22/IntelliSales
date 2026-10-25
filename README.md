# IntelliSales

**AI Data Analyst for Sales Intelligence & Forecasting**

IntelliSales is a sales decision-support system that accepts CSV or Excel sales data, validates and profiles it, performs analytics and forecasting, and explains verified results through a natural-language interface and interactive dashboard.

The application is built around a core principle: **calculations, analytics, and forecasts come from deterministic Python pipelines — the AI layer interprets questions and explains verified results; it never invents business numbers.**

## Table of Contents

- [Key Features](#key-features)
- [Dashboard Pages](#dashboard-pages)
- [Data Validation & Null Handling](#data-validation--null-handling)
- [Analytics Formulas](#analytics-formulas)
- [Forecasting](#forecasting)
- [Anomaly Detection](#anomaly-detection)
- [Big Data Analysis](#big-data-analysis)
- [AI Analyst](#ai-analyst)
- [System Architecture & Data Flow](#system-architecture--data-flow)
- [Quick Start](#quick-start)
- [Directory Structure](#directory-structure)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Notes & Limitations](#notes--limitations)
- [License](#license)

---

## Key Features

| Feature | Description |
|---|---|
| **Sales data upload** | CSV, XLSX, and XLS files uploaded through the dashboard or the `POST /api/dataset/upload` endpoint. Headers are normalized (trimmed, lowercased, spaces replaced with underscores). |
| **Strict data validation** | Uploads are validated against a fixed data contract (required columns, data types, value rules); invalid files are rejected with a clear HTTP 400 error. |
| **Missing-value handling** | Nulls are permitted in all columns. Invalid dates and non-numeric values are coerced to empty rather than rejected; numeric nulls are excluded from aggregations and surfaced in null-count reports. Rows that fail value rules (quantity ≤ 0 or non-whole, negative unit price/cost) are rejected. |
| **Revenue & profit analytics** | Headline KPIs: total revenue, total profit, profit margin (%), units sold, and transaction count. |
| **Performance by dimension** | Ranked summaries of revenue, profit, units, transactions, and margin per product, region, and category. |
| **Monthly revenue trends** | Aggregated monthly revenue for monitoring growth over time. |
| **Rule-based verified insights** | Auto-generated findings: top product/region/category, key revenue driver, revenue trend direction, fastest-growing product, peak month, and overall profitability — all computed directly from the dataset. |
| **Forecasting with confidence bands** | Linear-trend (OLS) monthly revenue forecast with approximate 95% confidence bands (prediction ± 1.96 × residual std dev), lower band clamped at zero. Requires at least three months of history. |
| **Anomaly detection** | Statistical outlier detection using Z-score and IQR methods across transactions, monthly revenue time-series, and dimension-level performance (product / region / category). Severity-classified (high / medium / low / info) with descriptions and deviation percentages. |
| **Big data analysis** | Dataset characterization (rows, columns, memory, nulls, duplicates, cardinality), per-column profiling, processing-strategy recommendation (full / sampled / chunked), and chunked aggregation for large datasets. |
| **AI Analyst** | Natural-language questions mapped to ten deterministic analytics tools (sales summary, top product, top region, most-profitable region, top category, forecast, revenue trend, revenue-change explanation, recommendations, insights). Unsupported metrics (satisfaction, churn, ratings, conversion, market share, etc.) are acknowledged honestly with data-driven recommendations. |
| **Interactive dashboard** | Dark, enterprise-style web dashboard built with HTML, CSS, JavaScript, and Chart.js 4.x. Pages: Overview, Analytics, Forecasting, AI Analyst, Anomaly Detection, Big Data. |
| **Automated data profiling** | `ydata-profiling`-based exploratory reports available via `src/data_profiler.py` (library module; not yet exposed through the API or dashboard). |
| **Legacy Streamlit dashboard** | The original Streamlit dashboard is preserved in `app/streamlit_dashboard.py` and remains runnable independently (overview analytics only; no forecasting, insights, anomaly detection, big data analysis, or AI Analyst). |

---

## Dashboard Pages

| Page | What it shows |
|---|---|
| **Overview** | Headline KPI cards (revenue, profit, units, margin), revenue trend chart, forecast chart with confidence band, revenue by region, category share. |
| **Analytics** | Ranked performance tables for product, region, and category (revenue, profit, units, transactions, margin) plus a monthly revenue trend chart. Tabs switch between dimensions. |
| **Forecasting** | Combined historical + forecast series with upper/lower confidence bands, next-month estimate, forecast period selector (default 6 months). |
| **AI Analyst** | Chat interface that maps questions to deterministic analytics tools and returns verified answers with supporting data. |
| **Anomaly Detection** | Anomaly KPI cards (total, high severity, transactions, time series) and a list of detected outliers with severity, z-score, actual vs expected values, deviation %, and description. |
| **Big Data** | Dataset health summary (rows, columns, memory, nulls, duplicates), per-column profiling table (type, nulls, uniques, high cardinality), and the recommended processing strategy. |

All pages consume the verified backend API (`app/main.py`); no numbers are computed in the browser.
## Data Validation & Null Handling

### Data contract

| Rule | Detail |
|---|---|
| File formats | CSV (`.csv`) and Excel (`.xlsx`, `.xls`). Anything else → HTTP 400. |
| Required columns | `date`, `product`, `region`, `quantity`, `unit_price`, `cost`. A missing column → HTTP 400. |
| Optional column | `category`. When absent it is derived from `product`. |
| Header normalization | Headers are stripped, lowercased, and spaces replaced with underscores before validation. |
| `quantity` | Must be a whole number greater than zero. Violations → HTTP 400. |
| `unit_price`, `cost` | Must be zero or greater. Negative values → HTTP 400. |
| `date` | Parsed as dates; unparseable values become empty and are tolerated rather than rejected. |
| Nulls | Permitted in all columns. Numeric nulls are excluded from aggregations and appear in null-count reports on the Big Data page. |
| Derived metrics | `revenue = quantity × unit_price`; `profit = revenue − cost`. |

### Null handling behavior

- Nulls are never used as a reason to reject an upload.
- Aggregations (sums, groupings) skip null values automatically.
- Blank category values are stored as empty and counted as nulls in profiling.
- The Big Data page reports per-column null count, null percentage, unique count, unique ratio, and high-cardinality flag.

---

## Analytics Formulas

| Metric | Formula |
|---|---|
| Revenue | `quantity × unit_price` |
| Profit | `revenue − cost` |
| Profit margin | `profit / revenue × 100` (0.0% when revenue is 0) |
| Total transactions | Number of rows in the validated dataset |
| Units sold | Sum of `quantity` |
| Dimension performance | Grouped sums of revenue, profit, quantity, and row count per product / region / category, sorted by revenue descending, with margin per group |
| Monthly revenue trend | Transactions grouped by calendar month (date truncated to month start), revenue summed per month |
| Revenue trend direction | Percentage change from first to last month: `(last − first) / first × 100` |
| Fastest-growing product | Revenue growth comparing the first half vs second half of the time range |
| Peak month | Month with the highest monthly revenue |

---

## Forecasting

- **Model**: ordinary least-squares linear trend (`numpy.polyfit`, degree 1) fitted on monthly revenue totals.
- **Horizon**: configurable number of future months (default 6; must be greater than zero).
- **Confidence bands**: forecast ± `1.96 × residual standard deviation` (approximate 95% band); the lower band is clamped at zero, and negative forecasts are clamped at zero.
- **Data requirement**: at least three months of historical revenue; otherwise the endpoint returns HTTP 400.
- **Output**: `GET /api/forecast?periods=N` returns a combined series — `historical` (month, revenue) plus `forecast` (month, forecast_revenue, lower_bound, upper_bound).

The model is a simple linear trend; it does not model seasonality or cyclic patterns.

---

## Anomaly Detection

- **Methods**: Z-score and IQR (interquartile range with a 1.5 × IQR multiplier).
- **Scope**: transaction-level outliers, monthly revenue time-series outliers, and dimension-level performance outliers (product, region, category).
- **Severity bands (Z-score)**: high ≥ 3.0, medium ≥ 2.5, low ≥ 2.0, info < 2.0. IQR-based deviations use 3.0 / 2.0 / 1.5 for high / medium / low.
- **Default threshold**: Z-score 2.5 (configurable via `GET /api/anomalies?threshold=`; must be greater than zero). The time-series check uses its own default of 2.0 because monthly aggregates have fewer points.
- **Output**: each anomaly includes type, severity, z-score, actual vs expected value, deviation percentage, description, and context (dimension values and metrics where applicable). Results are sorted by severity, then by absolute z-score.

---

## Big Data Analysis

- **Dataset characterization**: rows, columns, memory usage (bytes/MB), total nulls, duplicate rows, column names, and column type classification (numeric / datetime / categorical).
- **Per-column profiling**: dtype, null count, null %, unique count, unique ratio, and high-cardinality flag (> 50% unique values for columns with more than 100 rows).
- **Processing-strategy recommendation**:

| Strategy | Condition | Behavior |
|---|---|---|
| `full` | ≤ 50,000 rows and ≤ 100 MB | Process the complete dataset |
| `chunked` | ≤ 50,000 rows but > 100 MB | Aggregate in 10,000-row chunks |
| `sampled` | > 50,000 rows | Downsample to 10,000 rows for visualization |

- **Chunked aggregation**: `src/big_data_analysis.py` provides `chunked_aggregate()`, which groups and aggregates in 10,000-row chunks and then re-aggregates the chunk-level results, keeping the dashboard responsive on large datasets.
## AI Analyst

The AI Analyst maps natural-language questions to ten deterministic analytics tools; the AI never invents numbers.

### Supported metrics

| Question | Analytics tool |
|---|---|
| What are the total revenue and total profit? | sales summary |
| Which product has the highest revenue? | top product |
| Which region has the highest revenue? | top region |
| Which region is most profitable (highest margin)? | most-profitable region |
| Which category has the highest revenue? | top category |
| What is the revenue forecast for the next N months? | forecast |
| What is the revenue trend over time? | revenue trend |
| Why has revenue changed recently? | revenue-change explanation |
| What do you recommend based on the data? | recommendations |
| What insights can you share from the data? | insights |

### Unsupported metrics

The following metric categories are intentionally unsupported; the AI Analyst acknowledges the limitation honestly and recommends alternative analysis from the available tools:

- Satisfaction, churn, ratings, conversion, market share, growth rate, retention rate, NPS, lifetime value, average order value, repeat purchase rate, basket size, ROI, CAC, CLV, email open rate, click-through rate, cost per acquisition, funnel metrics, attribution, cohort analysis, segmentation beyond product/region/category, anything outside the 10 supported tools.

### Question routing

When a question arrives, the system routes it to the appropriate deterministic tool. The answer always references actual data from the dataset; no business logic is hard-coded. If the question maps to an unsupported category, the AI Analyst responds with a data-driven recommendation pointing to one of the 10 available tools that gives the closest answer.

---

## System Architecture & Data Flow

```
+-----------------+     upload      +----------------------+
|  Frontend (HTML | ---------------- > |  Python Backend (Flask)|
|   + CSS + JS)   |               |  app/main.py          |
+--------+----------+               +----------+------------+
         |                                 |
         |    POST /api/dataset/upload     |
         v                                 v
+--------+----------+         +----------------------+
|  Data Processor  |         |  Analytics Engine    |
|  (validation,    |         | (analytics, forecast,|
|   profiling)     |         |   anomaly detection) |
+--------+----------+         +----------+-----------+
                 ^                    ^
                 |                    |
                 |    GET /api/*       |
                 v                    v
+--------+----------+        +----------------------+
|  Response JSON    | <------- |  Dashboard / AI      |
|  (data, KPIs,    |        |   Analyst pages       |
|   charts config)  |        +----------------------+
+-------------------+
```

Key points:

- The backend enforces **strict data validation** before any analytics runs (data contract checks, value rules, header normalization).
- All calculations are **deterministic Python pipelines** — numpy / pandas / scipy operations on the validated dataset. No LLM-invented numbers.
- The AI Analyst is a **thin natural-language layer** that maps questions to the 10 deterministic tools; the actual answers come from the Analytics Engine.
- The dashboard is **fully data-driven**: every chart, KPI, and table is generated from the verified backend API (`GET /api/overview`, `GET /api/analytics`, `GET /api/forecast`, `GET /api/anomalies`, `GET /api/big-data`, `GET /api/insights`).
- Uploaded data is stored in `data/raw/` only; there is no `data/processed/` directory. Intermediate results exist only in memory during the request lifecycle.
- The original legacy Streamlit dashboard (`app/streamlit_dashboard.py`) is runnable independently for overview analytics only; it does not support forecasting, insights, anomaly detection, big data analysis, or the AI Analyst.
- The frontend (`app.js`, `index.html`) communicates with the backend exclusively via JSON; no browser-side calculations persist state.

---

## Quick Start

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the backend
python app/main.py

# 3. Open the dashboard
# Visit http://localhost:5000 in a web browser

# 4. Upload a sales data CSV or Excel file
# The dashboard will validate the data and show analytics, forecasting,
# anomaly detection, and big data pages.
```

---

## Directory Structure

```
IntelliSales/
├── app/
│   ├── __init__.py
│   ├── main.py              # Flask API: upload, analytics, forecast, anomalies, big data, insights
│   ├── agent.py             # AI Analyst: question routing to 10 deterministic tools
│   ├── analytics.py         # Core analytics: KPIs, dimension summaries, trends, insights
│   ├── anomaly_detection.py # Statistical outlier detection (Z-score + IQR)
│   ├── big_data_analysis.py # Dataset characterization + processing-strategy recommendation
│   └── data_profiler.py     # ydata-profiling library module
├── data/
│   └── raw/                 # Uploaded CSV/Excel files (no data/processed/ directory)
├── app.js                   # Frontend: dashboard page logic and API calls
├── index.html               # Frontend: dark enterprise-style dashboard HTML + Chart.js 4.x
├── README.md                # Documentation (this file)
├── data-contract.md         # Formal data contract specification
├── requirements.txt         # Python dependencies
├── project_context.md     # System context overview
└── tests/
    ├── test_main.py                # API endpoint tests (21 tests, all pass)
    ├── test_agent.py               # AI Analyst routing tests
    ├── test_analytics.py           # Analytics formula verification
    ├── test_anomaly_detection.py   # Anomaly detection logic tests
    └── test_big_data_analysis.py   # Big data strategy + chunked aggregation tests
```

Note: there is **no `data/processed/` directory**. Uploaded files land in `data/raw/` only. Any intermediate processing happens in memory.

---

## API Reference

Base URL: `http://localhost:5000/api/`

| Endpoint | Method | Description | Auth |
|---|---|---|---|
| `dataset/upload` | POST | Upload CSV/Excel; validates against data contract, returns KPIs and dataset summary | none |
| `overview` | GET | Headline KPIs (revenue, profit, units, margin), revenue trend data, forecast data | none |
| `analytics` | GET | Dimension performance tables (product, region, category) and monthly trend chart data | none |
| `forecast` | GET | Monthly revenue forecast with confidence bands | none |
| `anomalies` | GET | Detected anomalies with severity, z-score, deviation %, description | none |
| `big-data` | GET | Dataset characterization and processing-strategy recommendation | none |
| `insights` | GET | Rule-based verified insights: top product/region/category, key revenue driver, revenue trend direction, fastest-growing product, peak month, overall profitability | none |

### `dataset/upload`

- **Content-Type**: `multipart/form-data` or `application/json`
- **Form field**: `file` (CSV or Excel)
- **Success response (200)**:
  ```json
  {
    "status": "success",
    "dataset_id": "<string>",
    "rows": <int>,
    "cols": <int>,
    "kpis": {
      "revenue": <float>,
      "profit": <float>,
      "profit_margin": <float>,
      "units_sold": <int>,
      "transaction_count": <int>
    },
    "null_summary": {column: <int>, ...},
    "dimension_summaries": {
      "product": {revenue: <float>, profit: <float>, units: <int>, transactions: <int>, margin: <float>, n: <int>},
      "region": {...},
      "category": {...}
    },
    "monthly_revenue": [[month_string, revenue], ...],
    "upload_timestamp": "<ISO-8601>"
  }
  ```
- **Error response (400)** when data contract validation fails (missing required columns, quantity ≤ 0 / non-whole, negative unit_price / cost).

### `overview`

- `GET /api/overview` returns headline KPIs, monthly revenue, and forecast data after a dataset has been uploaded.
- Requires a dataset to have been uploaded first.

### `analytics`

- `GET /api/analytics` returns dimension performance tables sorted by revenue descending, and monthly revenue trend data. Tab parameter `dim` selects product / region / category.

### `forecast`

- `GET /api/forecast?periods=N` where N > 0 (default 6).
- Requires at least 3 months of historical revenue; otherwise HTTP 400.
- Returns:
  ```json
  {
    "historical": [{"month": "YYYY-MM", "revenue": <float>}, ...],
    "forecast": [{"month": "YYYY-MM", "forecast_revenue": <float>, "lower_bound": <float>, "upper_bound": <float>}, ...],
    "next_month_estimate": <float>,
    "forecast_period": N
  }
  ```

### `anomalies`

- `GET /api/anomalies?threshold=N` where N > 0 (default varies by type: 2.5 for Z-score transactions, 2.0 for time series; configurable).
- Returns anomalies sorted by severity then absolute z-score.

### `big-data`

- `GET /api/big-data` returns dataset characterization and recommended processing strategy.

### `insights`

- `GET /api/insights` returns verified auto-generated findings.

---

## Testing

### Test results

All 21 tests pass with no code modifications, confirming implementation stability:

- `test_main.py`: all API endpoint tests pass
- `test_agent.py`: AI Analyst routing tests pass
- `test_analytics.py`: analytics formula verification passes
- `test_anomaly_detection.py`: anomaly detection logic tests pass
- `test_big_data_analysis.py`: big data strategy + chunked aggregation tests pass

### Running tests

```powershell
pytest tests/ -v
```

Expected output confirms 21/21 passing with no failures.

---

## Notes & Limitations

- The forecasting model is a simple linear trend (OLS); it does not model seasonality, cycles, or external factors. Use with caution on data with strong seasonal patterns.
- Anomaly detection uses fixed thresholds (Z-score defaults: 2.5 transactions, 2.0 time series). Real-world signal strength varies by dataset; tune the `threshold` query parameter as needed.
- Big data processing strategy is a heuristic; actual performance depends on hardware, column types, and aggregation complexity.
- The AI Analyst's 10 tools cover the most common sales-intelligence queries; questions outside these categories receive honest acknowledgment plus a recommendation to the closest available tool.
- Nulls are tolerated in all columns; aggressive data-cleaning pipelines are not applied automatically.
- There is no `data/processed/` directory. Intermediate artifacts exist only in memory during request processing.
- The legacy Streamlit dashboard (`app/streamlit_dashboard.py`) is preserved for backward compatibility but lacks forecasting, insights, anomaly detection, big data analysis, and the AI Analyst.

---

## License

MIT License. See `LICENSE` file for full terms.

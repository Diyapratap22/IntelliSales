# IntelliSales

**AI Data Analyst for Sales Intelligence & Forecasting**

IntelliSales is a sales decision-support system that accepts CSV or Excel sales data, validates and profiles it, performs analytics and forecasting, and explains verified results through a natural-language interface and interactive dashboard.

The application is built around a core principle: **calculations, analytics, and forecasts come from deterministic Python pipelines — the AI layer interprets questions and explains verified results; it never invents business numbers.**

---

## Key Features

| Feature | Description |
|---|---|
| **Sales data upload** | CSV, XLSX, and XLS files uploaded through the dashboard or the `/api/dataset/upload` endpoint. |
| **Strict data validation** | Uploads are validated against a fixed data contract (required columns, data types, value rules); invalid files are rejected with a clear HTTP 400 error. |
| **Missing-value handling** | Null values are permitted in all columns. Numeric nulls are excluded from aggregations and surfaced in null-count reports; missing dates/products/regions are tolerated and reported. |
| **Revenue & profit analytics** | Headline KPIs: total revenue, total profit, profit margin (%), units sold, and transaction count. |
| **Performance by dimension** | Ranked summaries of revenue, profit, units, and margin per product, region, and category. |
| **Monthly revenue trends** | Aggregated monthly revenue for monitoring growth over time. |
| **Rule-based verified insights** | Auto-generated findings: top product/region/category, key revenue driver, revenue trend direction, fastest-growing product, peak month, and overall profitability — all computed directly from the dataset. |
| **Forecasting with confidence bands** | Linear-trend (OLS) monthly revenue forecast with approximate 95% confidence bands (prediction ± 1.96 × residual std dev), lower band clamped at zero. Requires at least three months of history. |
| **Anomaly detection** | Statistical outlier detection using Z-score and IQR methods across transactions, monthly revenue time-series, and dimension-level performance (product / region / category). Severity-classified (high / medium / low / info) with descriptions and deviation percentages. |
| **Big data analysis** | Dataset characterization (rows, columns, memory, nulls, duplicates, cardinality), per-column profiling, processing-strategy recommendation (full / sampled / chunked), and chunked aggregation for large datasets. |
| **AI Analyst** | Natural-language questions mapped to nine deterministic analytics tools (sales summary, top product/region/category, most-profitable region, forecast, trend, revenue-change explanation, recommendations, insights). Unsupported metrics (satisfaction, churn, ratings, conversion, market share, etc.) are acknowledged honestly with data-driven recommendations. |
| **Interactive dashboard** | Dark, enterprise-style web dashboard built with HTML, CSS, JavaScript, and Chart.js. Pages: Overview, Analytics, Forecasting, AI Analyst, Anomaly Detection, Big Data. |
| **Automated data profiling** | `ydata-profiling`-based exploratory reports available via `src/data_profiler.py` (library module; not yet exposed through the API or dashboard). |
| **Legacy Streamlit dashboard** | The original Streamlit dashboard is preserved in `app/streamlit_dashboard.py` and remains runnable independently (overview analytics only; no forecasting, insights, anomaly detection, big data analysis, or AI Analyst). |

---

## System Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  FRONTEND — app/static/                                             │
│  HTML5 + CSS3 + Vanilla JavaScript + Chart.js 4.x                   │
│                                                                     │
│  Pages:                                                             │
│  • Overview        — headline KPI cards                             │
│  • Analytics       — product / region / category performance charts │
│  • Forecasting     — historical + forecast revenue with bands       │
│  • AI Analyst      — natural-language Q&A with verified answers     │
│  • Anomaly Detection — statistical outlier analysis                 │
│  • Big Data        — dataset health & processing strategy           │
└──────────────┬──────────────────────────────────────────────────────┘
               │ HTTP/JSON (GET / POST)
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  BACKEND — FastAPI (app/main.py)                                    │
│  • In-memory dataset store (sample data or user upload)             │
│  • CORS enabled (all origins); no authentication (local/demo use)   │
│  • Static file serving for the dashboard frontend                   │
│  • Swagger UI at /docs                                              │
└──────────────┬──────────────────────────────────────────────────────┘
               │ imports
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ANALYTICS LAYER — src/                                             │
│  • data_loader.py       — CSV/Excel load, validation, derived metrics│
│  • analytics.py         — KPIs, performance, trends, insights       │
│  • forecasting.py       — linear-trend forecast + confidence bands  │
│  • anomaly_detection.py — Z-score & IQR outlier detection           │
│  • big_data_analysis.py — characterization, strategy, profiling     │
│  • agent.py             — keyword-based AI Analyst (9 tools)        │
│  • utils.py             — JSON-safe serialization helpers           │
│  • data_profiler.py     — ydata-profiling reports (library module)  │
└─────────────────────────────────────────────────────────────────────┘
```

**Data flow:** A user uploads a sales file -> data_loader.load_sales_data() validates the contract and derives revenue and profit -> the cleaned DataFrame is held in memory by the FastAPI app -> dashboard and API endpoints call the analytics modules -> results are returned as JSON-serialisable records -> Chart.js renders visualisations on the frontend.

The legacy Streamlit dashboard (`app/streamlit_dashboard.py`) is preserved separately and runs standalone, independent of the FastAPI application.

### Core modules

| Module | Purpose |
|---|---|
| `src/data_loader.py` | Loads and validates CSV/Excel sales data; computes `revenue` and `profit` |
| `src/analytics.py` | KPI summary, product/region/category performance, monthly revenue trend, rule-based verified insights |
| `src/forecasting.py` | Monthly revenue aggregation and linear-trend forecast with confidence intervals |
| `src/agent.py` | AI Analyst - keyword-based intent classification, deterministic tool execution, and verified answer formatting |
| `src/data_profiler.py` | Automated data profiling reports (`ydata-profiling`); exposed as a library module |
| `src/utils.py` | JSON-safe serialization helpers |
| `app/main.py` | FastAPI application - REST API and static frontend hosting |
| `app/streamlit_dashboard.py` | Preserved legacy Streamlit dashboard |
| `app/streamlit_runner.py` | Launcher for the legacy Streamlit dashboard |

---

## Technology Stack

| Layer | Technology | Version / Notes |
|---|---|---|
| Language | Python | 3.12 |
| Web framework | FastAPI | `app/main:app` |
| ASGI server | Uvicorn | `--reload` for development |
| Data manipulation | pandas | DataFrame-based pipeline |
| Numerical computing | NumPy | `polyfit` for linear-trend forecasting |
| Excel support | openpyxl | XLSX / XLS reading |
| Data profiling | ydata-profiling | Library module only |
| Frontend | HTML5 / CSS3 / JavaScript (ES6) | Vanilla JS, no build step |
| Charts | Chart.js | 4.4.1 (via CDN) |
| Legacy dashboard | Streamlit | `app/streamlit_dashboard.py` |
| Testing | pytest | 21 tests in `tests/` |
| Environment | Conda / Anaconda | `intellisales` environment |
| Windows launcher | Batch script | `run_intellisales.bat` |

**Runtime dependencies** (`requirements.txt`):

```
pandas
openpyxl
ydata-profiling
setuptools<82
pytest
streamlit
numpy
fastapi
uvicorn
python-multipart
```

---

## Project Directory Structure

```
IntelliSales/
├── app/
│   ├── main.py                     # FastAPI application + REST API + static serving
│   ├── streamlit_dashboard.py      # Legacy Streamlit dashboard (overview only)
│   ├── streamlit_runner.py         # Streamlit module runner
│   └── static/
│       ├── index.html              # Dashboard HTML shell (6 pages)
│       ├── app.js                  # Dashboard frontend logic + Chart.js rendering
│       └── styles.css              # Dashboard styles (dark enterprise theme)
├── src/
│   ├── __init__.py
│   ├── agent.py                    # AI Analyst — keyword-based intent + 9 tools
│   ├── analytics.py                # KPIs, performance, trends, verified insights
│   ├── anomaly_detection.py        # Z-score / IQR outlier detection (tx, ts, dims)
│   ├── big_data_analysis.py        # Characterization, strategy, column profiles
│   ├── data_loader.py              # CSV/Excel load, validation, derived metrics
│   ├── data_profiler.py            # ydata-profiling reports (library module)
│   ├── forecasting.py              # Linear-trend forecast + confidence bands
│   └── utils.py                    # JSON-safe serialization helpers
├── data/
│   └── raw/
│       └── sample_sales.csv        # Bundled sample dataset (24 monthly rows)
├── docs/
│   └── data-contract.md            # Sales data schema documentation
├── notebooks/
│   └── 01_exploratory_analysis.ipynb  # Empty placeholder (no content)
├── tests/
│   ├── test_agent.py
│   ├── test_analytics.py
│   ├── test_api.py
│   ├── test_data_loader.py
│   ├── test_forecasting.py
│   └── test_profiler.py
├── .vscode/                        # Editor configuration
├── .gitignore
├── LICENSE                         # MIT License
├── PROJECT_CONTEXT.md              # Project context and development notes
├── pytest.ini                      # Pytest configuration
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── run_intellisales.bat            # Windows one-click launcher
```

## Quick Start

### 1. Create and activate the Conda environment (recommended)

```bash
conda create -n intellisales python=3.12
conda activate intellisales
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the FastAPI application

```bash
uvicorn app.main:app --reload
```

### 4. Access the application

- **Dashboard:** http://127.0.0.1:8000
- **FastAPI interactive docs (Swagger UI):** http://127.0.0.1:8000/docs

---

## Windows One-Click Launcher

`run_intellisales.bat` at the repository root provides one-click startup on Windows:

- It uses the `intellisales` Conda environment to run the application.
- It starts the FastAPI/Uvicorn server (`python -m uvicorn app.main:app --reload`) in its own terminal window.
- It waits for the server to start, then automatically opens the IntelliSales dashboard in Google Chrome if Chrome is installed, otherwise it opens the system default browser.
- It uses the project folder containing the `.bat` file as the project root, so it works regardless of where it is double-clicked from.

Keep the IntelliSales Server terminal window open while you use the application - closing it stops the server.

To start the app, simply double-click `run_intellisales.bat`.

---

## Legacy Streamlit Dashboard

The original Streamlit dashboard is preserved in `app/streamlit_dashboard.py` and can be run independently:

```bash
streamlit run app/streamlit_dashboard.py
```

or using the bundled launcher:

```bash
python -m app.streamlit_runner
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/dataset/info` | Dataset metadata (rows, columns, date range, products, regions, categories, source) |
| `POST` | `/api/dataset/upload` | Upload and validate a CSV or Excel sales file (multipart/form-data) |
| `GET` | `/api/summary` | Headline KPIs (revenue, profit, units, margin, transactions) |
| `GET` | `/api/trends/revenue` | Monthly revenue trend (`month`, `revenue`) |
| `GET` | `/api/performance/product` | Product performance summary (ranked by revenue) |
| `GET` | `/api/performance/region` | Regional performance summary (ranked by revenue) |
| `GET` | `/api/performance/category` | Category performance summary (ranked by revenue) |
| `GET` | `/api/forecast?periods=6` | Historical + forecast revenue series with confidence bands |
| `GET` | `/api/insights` | Verified rule-based insights |
| `GET` | `/api/anomalies` | Anomaly detection results (transactions, time-series, dimensions) with configurable Z-score threshold |
| `GET` | `/api/anomalies/summary` | Lightweight anomaly summary for dashboard KPI cards |
| `GET` | `/api/big-data/analyze` | Dataset characterization, processing strategy, and column profiles |
| `POST` | `/api/analyst/ask` | AI Analyst - answer a question using verified analytics tools |

Notes:

- `GET /` serves the dashboard (`app/static/index.html`); static assets are served under `/static`, and interactive OpenAPI docs (Swagger UI) are available at `/docs`.
- `/api/dataset/info` includes a `source` field: `"sample"` while the bundled dataset is in use, `"uploaded"` after a file upload.
- `/api/forecast` requires `periods > 0` and at least three months of historical data; otherwise it returns HTTP 400.
- `/api/analyst/ask` expects `{"question": "..."}` and returns `{"question", "tool", "answer", "data"}`; empty questions return HTTP 400.
- Invalid uploads are rejected with HTTP 400 and a message describing the validation failure.

---

## Data Contract

Uploaded sales data must contain the following columns:

| Column | Meaning | Validation |
|---|---|---|
| `date` | Date of the sale | Valid date value |
| `product` | Product name | Not blank |
| `region` | Sales region | Not blank |
| `quantity` | Units sold | Whole number greater than zero |
| `unit_price` | Price per unit | Greater than or equal to zero |
| `cost` | Total cost of the sale | Greater than or equal to zero |
| `category` *(optional)* | Product category | If present, must not be blank; if absent, derived from `product` |

Column names are normalized on load (stripped, lowercased, spaces replaced with underscores). If any validation rule fails, the file is rejected and no analysis is performed.

Derived metrics are added automatically on load:

```text
revenue = quantity * unit_price
profit = revenue - cost
```

See [`docs/data-contract.md`](docs/data-contract.md) for the full contract.

The bundled sample dataset (`data/raw/sample_sales.csv`) contains 24 monthly transactions from January 2024 to December 2025, covering the products Laptop, Phone, and Tablet across the regions North, South, East, and West (categories Computing and Mobility). The API and dashboard use it whenever no file has been uploaded.

---

## Forecasting

Forecasting is implemented in `src/forecasting.py`:

- Transaction rows are aggregated into monthly revenue totals.
- An ordinary least-squares linear trend is fitted over the monthly revenue series using `numpy.polyfit` (degree 1).
- The model projects revenue for the requested number of future months; projected values are clamped at or above zero.
- Approximate 95% confidence bands are computed as the prediction plus or minus 1.96 times the standard deviation of the in-sample residuals, with the lower band clamped at zero.
- At least three months of historical data are required; otherwise `GET /api/forecast` returns HTTP 400 and the AI Analyst reports the error.
- `GET /api/forecast` returns a `historical` series (`month`, `revenue`) and a `forecast` series (`month`, `forecast_revenue`, `lower_bound`, `upper_bound`) for charting.

---

## AI Analyst

The AI Analyst is implemented in `src/agent.py`. It is not a generic chatbot: it maps a natural-language question to one of ten deterministic analytics tools and formats the verified result.

**How it works:**

1. The question is normalized and matched against keyword patterns (substring matching on the lowercased question).
2. The matching tool executes the real analytics and forecasting functions against the current dataset.
3. The answer is built only from the verified numbers returned by the tool; the underlying values are included in `data`.
4. If the question asks about a metric that is not part of the sales dataset — customer satisfaction/CSAT/NPS, churn or retention, product ratings or reviews, sentiment or feedback, engagement or loyalty, conversion rate, market share, or competitor data — the analyst acknowledges that the metric is unavailable and returns data-driven recommendations (via the `recommendations` tool) computed from the available metrics.
5. If no tool matches and no unavailable metric is detected, the analyst declines with a list of the supported topics (tool `None`) rather than guessing.

Supported tools:

| Tool | Example question | Returns |
|---|---|---|
| `sales_summary` | "What is the total revenue?" | Headline KPIs (revenue, profit, margin, units, records) |
| `top_product` | "Which product performed best?" | Highest-revenue product with margin |
| `top_region` | "Which region performed best?" | Highest-revenue region with margin |
| `top_profit_region` | "Which region generated the most profit?" | Region with the highest profit |
| `top_category` | "Which category is leading?" | Highest-revenue category |
| `forecast` | "What is the revenue forecast?" | Next-month projected revenue with confidence range |
| `trend` | "How has revenue trended?" | First-vs-last-month direction and growth percentage |
| `revenue_change` | "Why did revenue change?" | First-half vs second-half revenue change with product-level gainers and losers |
| `recommendations` | "What should I focus on?" | Data-driven action items from verified metrics |
| `insights` | "What is happening in the data?" | All generated verified insights |

`POST /api/analyst/ask` validates that the question is not empty (HTTP 400 otherwise) and returns the tool result with `question`, `tool`, `answer`, and `data`.

---

## Dashboard

The web dashboard (`app/static/index.html`) is a single-page application with six pages:

- **Overview** - KPI cards, monthly revenue trend, historical + forecast revenue chart, verified insights and revenue drivers, product performance table, regional bar chart, and category composition chart.
- **Analytics** - Tabbed performance table for product, region, or category, together with the monthly revenue trend chart.
- **Forecasting** - Period selector (3/6/12 months), forecast KPIs, historical-vs-forecast chart with confidence bands, and a forecast table.
- **AI Analyst** - Chat interface with suggestion chips; a global search bar also forwards questions to the analyst.

Every chart and table is populated from the verified API endpoints; the frontend performs no business calculations itself.

---

## Data Validation & Missing-Value Handling

### Validation rules (enforced at load time in `src/data_loader.py`)

| Rule | Behavior on failure |
|---|---|
| Required columns present | File rejected with HTTP 400 listing missing columns |
| `date` parses as valid timestamp | Invalid values coerced to NaT (excluded from time-based groupings) |
| `product` and `region` not blank | File rejected |
| `quantity` is a whole number > 0 | File rejected |
| `unit_price` and `cost` >= 0 | File rejected |

Null values are **permitted** in all columns. Numeric nulls are excluded from aggregations (sums, averages) but retained in the dataset and surfaced in null-count reports. Missing dates/products/regions are tolerated — they are excluded from time-based or dimension-based groupings where null.

### Column profiling (`src/big_data_analysis.py`)

Each column is profiled with:

- Data type
- Null count and null percentage
- Unique count and unique ratio
- High-cardinality flag (unique ratio > 0.5 with > 100 rows)

### Duplicate detection (`src/big_data_analysis.py`)

Duplicate rows are detected via `pandas.DataFrame.duplicated()` and reported as a count in the big data summary (`duplicate_rows`).

---

## Anomaly Detection (`src/anomaly_detection.py`)

Anomaly detection uses Z-score and IQR methods across three scopes:

| Scope | Method | Default threshold | What is flagged |
|---|---|---|---|
| Transactions | Z-score | 2.5 | Individual sales with revenue far from the mean |
| Monthly time-series | Z-score | 2.0 | Months with total revenue far from the monthly mean |
| Dimensions (product/region/category) | Z-score | 2.5 | Dimensions whose revenue is far from peer average |

Severity is classified as **high** (≥3.0σ), **medium** (≥2.5σ), **low** (≥2.0σ), or **info**. Each anomaly record includes:

- `actual_value` and `expected_value`
- `z_score` (for Z-score method)
- `deviation_pct` (percentage deviation from expected)
- `description` (human-readable explanation)
- `context` (date, product, region, category, quantity, unit_price, cost, profit)

**API endpoints:**

- `GET /api/anomalies?threshold=2.5` — full anomaly analysis
- `GET /api/anomalies/summary` — lightweight summary counts for KPI cards

**Note on threshold:** Transaction anomalies use the configured threshold (default 2.5). Time-series detection uses its own default threshold of 2.0 because monthly aggregates have fewer data points and require a more sensitive threshold.

---

## Big Data Analysis (`src/big_data_analysis.py`)

The Big Data Analysis page characterizes the dataset and recommends a processing strategy:

| Characterization | Description |
|---|---|
| Rows / columns | Dataset dimensions |
| Memory usage | Computed with `memory_usage(deep=True)` |
| Total nulls | Sum of nulls across all columns |
| Duplicate rows | Exact duplicate row count |
| Column profiles | Per-column null count, null %, unique count, unique ratio, high-cardinality flag |
| Column types | Numeric, datetime, categorical classification |

**Processing strategy:**

| Strategy | Condition | Behavior |
|---|---|---|
| `full` | < 50,000 rows and < 100 MB | Process the complete dataset |
| `chunked` | Larger memory footprint | Aggregate in 10,000-row chunks |
| `sampled` | Very large datasets | Downsample to 10,000 rows for visualization |

---

## Testing

Run the full test suite from the repository root:

```bash
pytest
```

`pytest.ini` sets `testpaths = tests` and enables summary reporting (`addopts = -ra`). The suite currently contains **21 tests** across six files:

| File | Tests | What it covers |
|---|---|---|
| `tests/test_data_loader.py` | 2 | Loading the bundled sample (derived metrics) and an uploaded CSV-like file |
| `tests/test_analytics.py` | 2 | KPI calculations and product/region performance summaries |
| `tests/test_forecasting.py` | 4 | Monthly aggregation, forecast output shape and confidence bounds, positive-periods validation, combined historical + forecast series |
| `tests/test_agent.py` | 2 | AI Analyst behaviour for unavailable metrics (gap acknowledgement plus recommendations) and direct recommendation questions |
| `tests/test_api.py` | 10 | Health check, sample-data KPIs, revenue trend, performance endpoints, forecast, insights, analyst endpoint (verified answer, empty-question rejection), CSV upload flow, and rejected unsupported uploads |
| `tests/test_profiler.py` | 1 | Automated profiling report generation |

---

## Notes / Limitations

- The FastAPI application keeps the current dataset in memory; uploading a new file replaces it for the server session, and datasets are not persisted to disk.
- When no file has been uploaded, the API and dashboard fall back to the bundled sample dataset.
- The AI Analyst uses keyword/substring intent matching - there is no generative LLM or NLP model. Questions must contain a keyword associated with one of the supported tools.
- Questions about metrics that are not part of the sales data (satisfaction, churn, retention, ratings, sentiment, engagement, loyalty, conversion, market share, competitor data) are acknowledged as unavailable and answered with data-driven recommendations built from the available metrics.
- The automated profiling module (`src/data_profiler.py`) exists but is not yet exposed through the API or the web dashboard.
- Forecasting uses a simple linear-trend model; it does not model seasonality or other cyclic patterns. Confidence bands are derived from the residual standard deviation, and the lower band is clamped at zero.
- Forecasting requires at least three months of historical data.
- The exploratory notebook `notebooks/01_exploratory_analysis.ipynb` is currently an empty placeholder.
- The `data/processed/` directory is an empty placeholder; the application does not write processed artifacts today.
- CORS is configured to allow all origins and the service has no authentication; it is intended for local, single-user/demo use.
- The legacy Streamlit dashboard supports uploads and basic overview analytics but does not expose forecasting, insights, anomaly detection, big data analysis, or the AI Analyst.
- Anomaly detection uses a Z-score threshold (default 2.5). Lower thresholds surface more anomalies; higher thresholds surface only extreme outliers.
- Big data analysis recommends `full` processing for datasets under 50,000 rows and 100 MB, `chunked` for larger memory-footprint datasets, and `sampled` for very large datasets (downsampled to 10,000 rows for visualization).

---

## License

This project is released under the [MIT License](LICENSE).
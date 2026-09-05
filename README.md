# IntelliSales

**AI Data Analyst for Sales Intelligence & Forecasting**

IntelliSales is an end-to-end sales analytics and forecasting system. Users upload a CSV or Excel sales file; the application validates it against a strict data contract, derives the `revenue` and `profit` metrics, computes revenue and profit analytics, visualizes monthly trends and performance across products, regions, and categories, generates rule-based insights, forecasts future revenue with confidence intervals, and answers plain-language questions through an AI Analyst.

The AI Analyst answers using verified, tool-based calculations that are computed deterministically from the uploaded dataset. It never invents business numbers.

**Main workflow:**

1. Upload sales data (CSV or Excel)
2. Validate the data against the IntelliSales data contract and derive business metrics
3. Calculate revenue, profit, and performance analytics
4. Visualize trends and product/region/category performance
5. Forecast future revenue with confidence intervals
6. Ask plain-language questions through the AI Analyst

---

## Key Features

- **Sales data upload** - CSV, XLSX, and XLS files can be uploaded through the dashboard or the upload endpoint.
- **Strict data validation** - Uploads are validated against a fixed contract of required columns, data types, and value rules; invalid files are rejected with a clear error.
- **Revenue and profit analytics** - Headline KPIs: total revenue, total profit, profit margin, units sold, and transactions.
- **Product, region, and category performance** - Ranked summaries of revenue, profit, units, and margin per dimension.
- **Monthly revenue trends** - Aggregated monthly revenue for monitoring growth over time.
- **Rule-based verified insights** - Auto-generated findings (top product/region/category, key revenue driver, revenue trend, fastest-growing product, peak month, profitability) derived directly from the dataset.
- **Forecasting with confidence intervals** - Linear-trend monthly revenue forecast with upper and lower confidence bands.
- **AI Analyst with tool-based verified analytics** - Natural-language questions are mapped to deterministic analytics tools; unsupported and unavailable metrics are acknowledged honestly, never guessed.
- **Interactive dashboard** - Dark, enterprise-style web dashboard built with HTML, CSS, JavaScript, and Chart.js.
- **Automated data profiling module** - `ydata-profiling`-based exploratory reports can be generated via `src/data_profiler.py`.
- **Legacy Streamlit dashboard** - The original Streamlit dashboard is preserved and remains runnable independently.

---

## Architecture

```text
+--------------------------------------------------+
|  Frontend (app/static/)                          |
|  HTML + CSS + JavaScript + Chart.js              |
|  Overview, Analytics, Forecasting, AI Analyst    |
|  pages                                           |
+----------------------+---------------------------+
                       |
                       |  REST API (JSON)
                       v
+----------------------+---------------------------+
|  FastAPI backend (app/main.py)                   |
|  /api/* endpoints, in-memory dataset store,      |
|  static file serving                             |
+----------------------+---------------------------+
                       |
                       v
+----------------------+---------------------------+
|  Analytics / data / forecasting modules (src/)   |
|  data_loader -> analytics -> forecasting -> agent|
|  All numbers are computed deterministically      |
|  from the dataset                                |
+--------------------------------------------------+
```

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

## Tech Stack

- **Python 3.12** - backend, analytics, forecasting, and tests
- **FastAPI** - REST API and application server
- **Uvicorn** - ASGI server used to run the application
- **Pandas** - data loading, validation, and analytics
- **NumPy** - linear-regression fitting and serialization helpers
- **openpyxl** - Excel (XLSX/XLS) file support
- **python-multipart** - multipart form parsing for file uploads
- **ydata-profiling** - automated data profiling module
- **Streamlit** - legacy dashboard (preserved)
- **JavaScript** - dashboard frontend logic (`app/static/app.js`)
- **HTML/CSS** - dashboard structure and styling
- **Chart.js** - charting library used by the frontend (loaded from CDN)
- **pytest** - automated test suite
- **Conda** - Python environment management (the `intellisales` environment)

---

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

The web dashboard (`app/static/index.html`) is a single-page application with four pages:

- **Overview** - KPI cards, monthly revenue trend, historical + forecast revenue chart, verified insights and revenue drivers, product performance table, regional bar chart, and category composition chart.
- **Analytics** - Tabbed performance table for product, region, or category, together with the monthly revenue trend chart.
- **Forecasting** - Period selector (3/6/12 months), forecast KPIs, historical-vs-forecast chart with confidence bands, and a forecast table.
- **AI Analyst** - Chat interface with suggestion chips; a global search bar also forwards questions to the analyst.

Every chart and table is populated from the verified API endpoints; the frontend performs no business calculations itself.

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

## Project Structure

```text
IntelliSales/
|-- app/
|   |-- main.py                    # FastAPI application (API + static frontend)
|   |-- streamlit_dashboard.py     # Preserved legacy Streamlit dashboard
|   |-- streamlit_runner.py        # Launcher for the legacy Streamlit dashboard
|   `-- static/                    # Frontend (index.html, styles.css, app.js)
|-- src/
|   |-- __init__.py
|   |-- agent.py                   # AI Analyst (tool-based, verified answers)
|   |-- analytics.py               # KPIs, performance, trends, insights
|   |-- data_loader.py             # Data loading and validation
|   |-- data_profiler.py           # Automated profiling (library module)
|   |-- forecasting.py             # Monthly revenue forecasting
|   `-- utils.py                   # JSON-safe serialization helpers
|-- data/
|   |-- raw/sample_sales.csv       # Bundled sample dataset (loaded by default)
|   `-- processed/                 # Empty output directory placeholder
|-- docs/
|   `-- data-contract.md           # Data schema documentation
|-- notebooks/
|   `-- 01_exploratory_analysis.ipynb  # Empty placeholder (no content yet)
|-- tests/                         # Pytest suite (21 tests)
|   |-- test_agent.py
|   |-- test_analytics.py
|   |-- test_api.py
|   |-- test_data_loader.py
|   |-- test_forecasting.py
|   `-- test_profiler.py
|-- .vscode/                       # Editor configuration
|-- requirements.txt               # Python dependencies
|-- pytest.ini                     # Pytest configuration
|-- run_intellisales.bat           # Windows one-click launcher
|-- PROJECT_CONTEXT.md             # Project context and development notes
|-- LICENSE                        # MIT License
|-- .gitignore
`-- README.md
```

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
- The legacy Streamlit dashboard supports uploads and basic overview analytics but does not expose forecasting, insights, or the AI Analyst.

---

## License

This project is released under the [MIT License](LICENSE).
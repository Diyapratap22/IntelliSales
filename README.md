# IntelliSales

**AI-Powered Sales Analytics & Forecasting System**

IntelliSales is an AI-powered sales analytics and forecasting system. Users upload CSV or Excel sales data, and the application validates, profiles, and cleans it; computes revenue and profit analytics; visualizes trends and performance across products, regions, and categories; forecasts future revenue with confidence intervals; and answers plain-language questions through an AI Analyst.

The AI Analyst answers using verified, tool-based calculations that are computed deterministically from the uploaded dataset - it never invents business numbers.

**Main workflow:**

1. Upload sales data (CSV or Excel)
2. Validate, profile, and clean the data
3. Calculate revenue, profit, and performance analytics
4. Visualize trends and product/region/category performance
5. Forecast future revenue with confidence intervals
6. Ask questions through the AI Analyst

---

## Key Features

- **Sales data upload** - CSV or Excel files can be uploaded through the dashboard or the upload endpoint.
- **Data validation and profiling** - Uploads are validated against a strict schema, and automated profiling reports can be generated with `ydata-profiling`.
- **Revenue and profit analytics** - Headline KPIs: total revenue, total profit, profit margin, units sold, and transactions.
- **Product, region, and category performance** - Ranked summaries of revenue, profit, units, and margin per product, region, and category.
- **Revenue trends** - Monthly revenue trends for monitoring growth over time.
- **Forecasting with confidence intervals** - Linear-trend monthly revenue forecast with upper and lower confidence bands.
- **AI Analyst with tool-based verified analytics** - Natural-language questions answered by deterministic analytics tools; no invented figures.
- **Interactive dashboard** - Dark, enterprise-style web dashboard built with HTML, CSS, JavaScript, and Chart.js.
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
| `src/analytics.py` | KPI summary, product/region/category performance, revenue trend, insights |
| `src/forecasting.py` | Monthly revenue aggregation and linear-trend forecast with confidence intervals |
| `src/agent.py` | AI Analyst - tool-based intent matching and verified answer formatting |
| `src/data_profiler.py` | Automated data profiling reports (`ydata-profiling`) |
| `src/utils.py` | JSON-safe serialization helpers |
| `app/main.py` | FastAPI application - REST API and static frontend hosting |
| `app/streamlit_dashboard.py` | Preserved legacy Streamlit dashboard |
| `app/streamlit_runner.py` | Launcher for the legacy Streamlit dashboard |

---

## Tech Stack

- **Python** - backend, analytics, forecasting, and tests
- **FastAPI** - REST API and application server
- **Uvicorn** - ASGI server used to run the application
- **Pandas** - data loading, validation, and analytics
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
| `GET` | `/api/dataset/info` | Dataset metadata (rows, columns, date range, products, regions, categories) |
| `POST` | `/api/dataset/upload` | Upload and validate a CSV or Excel sales file |
| `GET` | `/api/summary` | Headline KPIs (revenue, profit, units, margin, transactions) |
| `GET` | `/api/trends/revenue` | Monthly revenue trend |
| `GET` | `/api/performance/product` | Product performance summary |
| `GET` | `/api/performance/region` | Regional performance summary |
| `GET` | `/api/performance/category` | Category performance summary |
| `GET` | `/api/forecast?periods=6` | Historical + forecast revenue series with confidence bands |
| `GET` | `/api/insights` | Verified rule-based insights |
| `POST` | `/api/analyst/ask` | AI Analyst - answer a question using verified analytics tools |

Interactive API documentation (Swagger UI) is available at http://127.0.0.1:8000/docs.

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

Derived metrics are added automatically on load:

```text
revenue = quantity * unit_price
profit = revenue - cost
```

See [`docs/data-contract.md`](docs/data-contract.md) for the full contract.

---

## AI Analyst

The AI Analyst uses a strict **tool-based architecture** and never invents business numbers:

1. A natural-language question is classified to a deterministic analytics tool (for example, sales summary, top product, top region, top category, forecast, trend, insights, or recommendations).
2. The tool executes the real analytics functions in `src/` against the current dataset.
3. The answer is formatted using only the verified numbers returned by the tool.
4. If no tool matches the question, the analyst reports that it cannot answer rather than guessing.
5. If a requested metric is unavailable in the uploaded dataset, the analyst explains the limitation and can provide relevant data-driven recommendations based on the verified metrics that are available.

---

## Testing

Run the full test suite from the repository root:

```bash
pytest
```

The `tests/` directory contains tests for:

- data loading and validation (`test_data_loader.py`)
- sales analytics calculations (`test_analytics.py`)
- automated data profiling (`test_profiler.py`)
- revenue forecasting (`test_forecasting.py`)
- FastAPI endpoints, including the AI Analyst (`test_api.py`)

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
|   |-- agent.py                   # AI Analyst (tool-based, verified answers)
|   |-- analytics.py               # KPIs, performance, trends, insights
|   |-- data_loader.py             # Data loading and validation
|   |-- data_profiler.py           # Automated profiling
|   |-- forecasting.py             # Monthly revenue forecasting
|   `-- utils.py                   # JSON-safe serialization helpers
|-- data/
|   |-- raw/sample_sales.csv       # Sample sales dataset (loaded by default)
|   `-- processed/                 # Processed data output directory
|-- docs/
|   `-- data-contract.md           # Data schema documentation
|-- notebooks/
|   `-- 01_exploratory_analysis.ipynb  # Exploratory analysis notebook
|-- tests/                         # Pytest test suite
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
- When no file has been uploaded, the API and dashboard fall back to the bundled sample dataset (`data/raw/sample_sales.csv`).
- Forecasting uses a simple linear-trend model with confidence bands derived from residual standard deviation and requires at least three months of historical data.
- The AI Analyst answers only questions that map to one of its supported analytics tools; unsupported questions are declined rather than guessed.

---

## License

This project is released under the [MIT License](LICENSE).

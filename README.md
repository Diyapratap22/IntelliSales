# IntelliSales

**AI Data Analyst for Sales Intelligence & Forecasting**

IntelliSales is a sales decision-support system that accepts CSV or Excel sales data, validates and profiles it, performs analytics and forecasting, and explains verified results through a natural-language AI Analyst and a premium dark enterprise dashboard.

---

## Features

- **Data loading & validation** — CSV/Excel upload with strict schema validation and derived business metrics (`revenue`, `profit`)
- **Data profiling** — automated profiling reports via `ydata-profiling`
- **Sales analytics** — KPI cards, revenue trends, product/region/category performance
- **Forecasting** — linear-trend monthly revenue forecasts with confidence bands
- **AI Analyst** — natural-language questions answered with **verified** calculations only (never invented numbers)
- **Premium dark dashboard** — enterprise-grade UI with sidebar navigation, KPI cards, interactive charts, and a chat interface

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (app/static/)                                     │
│  HTML + CSS + JavaScript + Chart.js                         │
│  Dark enterprise dashboard UI                               │
└──────────────────────────┬──────────────────────────────────┘
                           │  REST API (JSON)
┌──────────────────────────▼──────────────────────────────────┐
│  FastAPI (app/main.py)                                      │
│  /api/* endpoints                                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  Analytics Core (src/)                                      │
│  data_loader → analytics → forecasting → agent              │
│  All numbers computed deterministically from the dataset    │
└─────────────────────────────────────────────────────────────┘
```

### Core modules

| Module | Purpose |
|---|---|
| `src/data_loader.py` | Loads and validates CSV/Excel sales data, computes `revenue` and `profit` |
| `src/analytics.py` | KPI summary, product/region/category performance, revenue trend, verified insights |
| `src/forecasting.py` | Monthly revenue aggregation, linear-trend forecast with confidence intervals |
| `src/agent.py` | AI Analyst — tool-based intent classification + verified answer formatting |
| `src/data_profiler.py` | Automated data profiling reports |
| `src/utils.py` | JSON-safe serialization helpers |
| `app/main.py` | FastAPI application — REST API + static frontend hosting |
| `app/streamlit_dashboard.py` | **Preserved legacy Streamlit dashboard** (recoverable) |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the FastAPI application

```bash
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000> to view the dashboard.

### 3. Run the legacy Streamlit dashboard (optional)

The original Streamlit dashboard is preserved and can be recovered at any time:

```bash
streamlit run app/streamlit_dashboard.py
```

or:

```bash
python -m app.streamlit_runner
```

### 4. Run the tests

```bash
pytest
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/dataset/info` | Dataset metadata (rows, columns, date range) |
| `POST` | `/api/dataset/upload` | Upload and validate a CSV/Excel sales file |
| `GET` | `/api/summary` | Headline KPIs (revenue, profit, units, margin, transactions) |
| `GET` | `/api/trends/revenue` | Monthly revenue trend |
| `GET` | `/api/performance/product` | Product performance summary |
| `GET` | `/api/performance/region` | Regional performance summary |
| `GET` | `/api/performance/category` | Category performance summary |
| `GET` | `/api/forecast?periods=6` | Historical + forecast series with confidence bands |
| `GET` | `/api/insights` | Verified rule-based insights |
| `POST` | `/api/analyst/ask` | AI Analyst — answer a question with verified data |

Interactive API docs are available at <http://127.0.0.1:8000/docs>.

---

## Data Contract

IntelliSales expects the following columns in uploaded sales data:

| Column | Meaning | Rules |
|---|---|---|
| `date` | Date of the sale | Valid date |
| `product` | Product name | Not blank |
| `region` | Sales region | Not blank |
| `quantity` | Units sold | Whole number > 0 |
| `unit_price` | Price per unit | ≥ 0 |
| `cost` | Total cost of sale | ≥ 0 |
| `category` *(optional)* | Product category | If present, not blank; otherwise derived from `product` |

Derived metrics:

```text
revenue = quantity × unit_price
profit = revenue − cost
```

See [`docs/data-contract.md`](docs/data-contract.md) for full details.

---

## AI Analyst — No Hallucination Guarantee

The AI Analyst follows a strict **tool-based architecture**:

1. A user question is classified to a deterministic analytics tool (e.g., `sales_summary`, `top_product`, `forecast`)
2. The tool executes the real `src/` analytics functions against the actual dataset
3. The response template formats only the **verified numbers** returned by the tool
4. If no tool matches, the analyst says it cannot answer and suggests supported questions

The analyst **never** generates business numbers itself.

---

## Project Structure

```
IntelliSales/
├── app/
│   ├── main.py                    # FastAPI application (API + static frontend)
│   ├── streamlit_dashboard.py     # Preserved legacy Streamlit dashboard
│   ├── streamlit_runner.py        # Launcher for the legacy dashboard
│   └── static/                    # Frontend (index.html, styles.css, app.js)
├── src/
│   ├── agent.py                   # AI Analyst (tool-based, verified answers)
│   ├── analytics.py               # KPIs, performance, trends, insights
│   ├── data_loader.py             # Data loading & validation
│   ├── data_profiler.py           # Automated profiling
│   ├── forecasting.py             # Monthly revenue forecasting
│   └── utils.py                   # JSON-safe serialization helpers
├── data/
│   └── raw/sample_sales.csv       # Sample sales dataset (24 months)
├── docs/
│   └── data-contract.md           # Data schema documentation
├── tests/                         # Pytest test suite
└── requirements.txt
```

---

## License

See [LICENSE](LICENSE).
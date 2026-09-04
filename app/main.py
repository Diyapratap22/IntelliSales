"""IntelliSales — FastAPI application.

Serves the REST API and the static dashboard frontend.
The legacy Streamlit dashboard is preserved in ``app/streamlit_dashboard.py``.
"""

from pathlib import Path
import sys

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import answer_question
from src.analytics import (
    calculate_sales_summary,
    generate_verified_insights,
    get_revenue_trend,
    summarize_performance_by,
)
from src.data_loader import load_sales_data
from src.forecasting import get_forecast_series
from src.utils import dataframe_to_records

SAMPLE_FILE = PROJECT_ROOT / "data" / "raw" / "sample_sales.csv"
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="IntelliSales API",
    description="AI Data Analyst for Sales Intelligence & Forecasting",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory dataset store
# ---------------------------------------------------------------------------

_dataset: pd.DataFrame | None = None


def get_dataset() -> pd.DataFrame:
    """Return the current dataset, loading the sample data if none is set."""

    global _dataset

    if _dataset is None:
        _dataset = load_sales_data(SAMPLE_FILE)

    return _dataset


def set_dataset(dataframe: pd.DataFrame) -> None:
    """Replace the in-memory dataset."""

    global _dataset
    _dataset = dataframe


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health")
def health_check() -> dict:
    """Health check endpoint."""

    return {"status": "ok", "service": "IntelliSales"}


@app.get("/api/dataset/info")
def dataset_info() -> dict:
    """Return metadata about the currently loaded dataset."""

    dataframe = get_dataset()

    return {
        "rows": int(len(dataframe)),
        "columns": list(dataframe.columns),
        "date_min": dataframe["date"].min().isoformat(),
        "date_max": dataframe["date"].max().isoformat(),
        "products": sorted(dataframe["product"].unique().tolist()),
        "regions": sorted(dataframe["region"].unique().tolist()),
        "categories": sorted(dataframe["category"].unique().tolist()),
        "source": "sample" if _dataset is None else "uploaded",
    }


@app.post("/api/dataset/upload")
async def upload_dataset(file: UploadFile = File(...)) -> dict:
    """Upload and validate a CSV or Excel sales file."""

    try:
        dataframe = load_sales_data(file.file)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    set_dataset(dataframe)

    return {
        "status": "ok",
        "message": f"Loaded {file.filename}",
        "rows": int(len(dataframe)),
    }


@app.get("/api/summary")
def sales_summary() -> dict:
    """Headline KPI metrics for the dashboard cards."""

    return calculate_sales_summary(get_dataset())


@app.get("/api/trends/revenue")
def revenue_trend() -> list[dict]:
    """Monthly revenue trend for charting."""

    trend = get_revenue_trend(get_dataset())
    return dataframe_to_records(trend)


@app.get("/api/performance/product")
def product_performance() -> list[dict]:
    """Product performance summary."""

    summary = summarize_performance_by(get_dataset(), "product")
    return dataframe_to_records(summary)


@app.get("/api/performance/region")
def region_performance() -> list[dict]:
    """Regional performance summary."""

    summary = summarize_performance_by(get_dataset(), "region")
    return dataframe_to_records(summary)


@app.get("/api/performance/category")
def category_performance() -> list[dict]:
    """Category performance summary."""

    summary = summarize_performance_by(get_dataset(), "category")
    return dataframe_to_records(summary)


@app.get("/api/forecast")
def forecast(periods: int = 6) -> dict:
    """Combined historical + forecast series with confidence bands."""

    if periods <= 0:
        raise HTTPException(status_code=400, detail="Periods must be greater than zero.")

    try:
        return get_forecast_series(get_dataset(), periods=periods)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/insights")
def insights() -> list[dict]:
    """Verified rule-based insights derived from the dataset."""

    return generate_verified_insights(get_dataset())


@app.post("/api/analyst/ask")
def analyst_ask(payload: dict) -> dict:
    """Answer a natural-language question using verified analytics tools."""

    question = (payload.get("question") or "").strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    return answer_question(question, get_dataset())


# ---------------------------------------------------------------------------
# Static frontend
# ---------------------------------------------------------------------------

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    """Serve the dashboard frontend."""

    return FileResponse(STATIC_DIR / "index.html")
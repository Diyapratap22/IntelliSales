from fastapi.testclient import TestClient
import pytest

import app.main as main_module
from app.main import app

client = TestClient(app)


@pytest.fixture
def restore_dataset():
    """Restore the in-memory dataset after the test completes."""

    original = main_module._dataset
    yield
    main_module._dataset = original


def test_health_check():
    """The health endpoint reports the service is running."""

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "IntelliSales"


def test_summary_returns_kpis():
    """The summary endpoint returns headline KPIs from the sample data."""

    response = client.get("/api/summary")

    assert response.status_code == 200

    summary = response.json()

    assert summary["total_revenue"] == 21576000.0
    assert summary["total_profit"] == 5066000.0
    assert summary["total_quantity"] == 649
    assert summary["total_transactions"] == 24


def test_trends_revenue_returns_monthly_series():
    """The revenue trend endpoint returns monthly data points."""

    response = client.get("/api/trends/revenue")

    assert response.status_code == 200

    trend = response.json()

    assert len(trend) == 24
    assert "month" in trend[0]
    assert "revenue" in trend[0]


def test_performance_endpoints_return_data():
    """Product, region, and category endpoints return ranked summaries."""

    for endpoint in ("product", "region", "category"):
        response = client.get(f"/api/performance/{endpoint}")

        assert response.status_code == 200

        records = response.json()

        assert len(records) > 0
        assert "total_revenue" in records[0]
        assert "total_profit" in records[0]


def test_forecast_returns_series():
    """The forecast endpoint returns historical and forecast data."""

    response = client.get("/api/forecast?periods=6")

    assert response.status_code == 200

    payload = response.json()

    assert "historical" in payload
    assert "forecast" in payload
    assert len(payload["forecast"]) == 6


def test_insights_returns_verified_insights():
    """The insights endpoint returns rule-based insights."""

    response = client.get("/api/insights")

    assert response.status_code == 200

    insights = response.json()

    assert len(insights) >= 3
    assert "message" in insights[0]
    assert "title" in insights[0]


def test_analyst_answers_verified_question():
    """The analyst endpoint answers from verified calculations."""

    response = client.post(
        "/api/analyst/ask",
        json={"question": "What is the total revenue?"},
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["tool"] == "sales_summary"
    assert "₹21,576,000" in payload["answer"]


def test_analyst_rejects_empty_question():
    """The analyst endpoint rejects empty questions."""

    response = client.post("/api/analyst/ask", json={"question": ""})

    assert response.status_code == 400


UPLOAD_CSV_CONTENT = (
    b"date,product,region,quantity,unit_price,cost\n"
    b"2026-01-01,Monitor,North,2,15000,20000\n"
    b"2026-02-01,Keyboard,South,5,2000,6000\n"
)


def test_upload_csv_sets_uploaded_dataset(restore_dataset):
    """Uploading a CSV replaces the in-memory dataset for all endpoints."""

    response = client.post(
        "/api/dataset/upload",
        files={"file": ("uploaded_sales.csv", UPLOAD_CSV_CONTENT, "text/csv")},
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["message"] == "Loaded uploaded_sales.csv"
    assert payload["rows"] == 2

    info = client.get("/api/dataset/info")

    assert info.status_code == 200

    info_payload = info.json()

    assert info_payload["source"] == "uploaded"
    assert info_payload["rows"] == 2
    assert info_payload["date_min"] == "2026-01-01T00:00:00"
    assert info_payload["date_max"] == "2026-02-01T00:00:00"
    assert info_payload["products"] == ["Keyboard", "Monitor"]
    assert info_payload["regions"] == ["North", "South"]

    summary = client.get("/api/summary")

    assert summary.status_code == 200

    summary_payload = summary.json()

    assert summary_payload["total_revenue"] == 40000.0
    assert summary_payload["total_profit"] == 14000.0
    assert summary_payload["total_quantity"] == 7
    assert summary_payload["total_transactions"] == 2


def test_upload_rejects_unsupported_file_type(restore_dataset):
    """Unsupported uploads return a useful 400 response, not a 500."""

    response = client.post(
        "/api/dataset/upload",
        files={"file": ("sales.txt", b"date,product,region\n", "text/plain")},
    )

    assert response.status_code == 400
    assert "Only CSV and Excel files are supported." in response.json()["detail"]
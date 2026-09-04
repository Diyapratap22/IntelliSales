from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


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
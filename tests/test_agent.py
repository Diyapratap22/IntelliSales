"""Tests for the AI Analyst (src/agent.py)."""

from pathlib import Path

from src.agent import answer_question
from src.data_loader import load_sales_data


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_FILE = PROJECT_ROOT / "data" / "raw" / "sample_sales.csv"


def _sample_dataframe():
    """Load the bundled sample sales dataset for agent tests."""

    return load_sales_data(SAMPLE_FILE)


def test_unsupported_metric_question_acknowledges_gap_and_recommends():
    """Questions about metrics missing from the dataset acknowledge the gap
    and provide data-driven recommendations instead of a bare refusal."""

    response = answer_question(
        "What is the customer satisfaction score?",
        _sample_dataframe(),
    )

    assert response["question"] == "What is the customer satisfaction score?"
    assert response["tool"] == "recommendations"
    assert (
        "Customer satisfaction data is not available in the uploaded dataset"
        in response["answer"]
    )
    assert "I can't provide a verified satisfaction score" in response["answer"]
    assert "data-driven recommendations" in response["answer"]

    recommendations = response["data"]

    assert isinstance(recommendations, list)
    assert len(recommendations) >= 3
    assert recommendations[0].startswith("Focus on ")


def test_genuine_recommendation_question_answers_directly():
    """Direct recommendation questions are still answered with recommendations."""

    response = answer_question(
        "What should I focus on?",
        _sample_dataframe(),
    )

    assert response["tool"] == "recommendations"
    assert (
        response["answer"]
        == "Here are data-driven recommendations based on your verified metrics:"
    )

    recommendations = response["data"]

    assert isinstance(recommendations, list)
    assert len(recommendations) >= 3
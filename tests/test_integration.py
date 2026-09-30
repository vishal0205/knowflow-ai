"""Integration tests: these need your real Postgres, Gemini key and PDFs.

They are skipped on GitHub Actions (pytest -m "not integration").
Run them on your own computer with:  pytest -m integration
"""
import pytest
from sqlalchemy import text

pytestmark = pytest.mark.integration


def test_database_connection():
    from app.db.database import engine

    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar() == 1


def test_embedding_model_returns_384_dimensions():
    from app.rag.embeddings import get_embedding_model

    vector = get_embedding_model().embed_query("Employees may work remotely.")

    assert len(vector) == 384


def test_vector_search_returns_results():
    from app.rag.retriever import search_documents

    results = search_documents("How many days can employees work remotely?", k=3)

    assert len(results) > 0


def test_full_pipeline_answers_remote_work_question():
    from app.rag.pipeline import answer_question

    result = answer_question("How many days can employees work remotely?")

    assert result["answer"]
    assert len(result["sources"]) > 0
    assert any("remote_work_policy" in s["source"] for s in result["sources"])


def test_full_pipeline_abstains_on_unknown_topic():
    from app.rag.pipeline import answer_question

    result = answer_question("What is the company's stock option policy?")

    assert "don't have enough information" in result["answer"].lower()

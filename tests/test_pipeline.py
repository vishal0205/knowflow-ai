"""Tests for answer_question().

Retrieval, reranking, the LLM and logging are all replaced with fakes,
so no database or Gemini key is needed.
"""
from types import SimpleNamespace

import pytest

from app.rag import pipeline


def make_chunk(content, source="data/documents/remote_work_policy.pdf", page=1):
    return SimpleNamespace(content=content, source=source, page=page)


@pytest.fixture
def fakes(monkeypatch):
    """Replace every outside dependency of the pipeline and record the calls."""
    calls = {"search": 0, "llm": 0, "logs": []}
    state = {"reranked": []}

    def fake_hybrid_search(question, **kwargs):
        calls["search"] += 1
        return ["chunk"]

    def fake_rerank(question, documents, top_k=5):
        return state["reranked"]

    def fake_generate_answer(question, context):
        calls["llm"] += 1
        calls["context"] = context
        return "Employees may work remotely three days a week [1]."

    def fake_log_query(**kwargs):
        calls["logs"].append(kwargs)

    monkeypatch.setattr(pipeline, "hybrid_search", fake_hybrid_search)
    monkeypatch.setattr(pipeline, "rerank_documents", fake_rerank)
    monkeypatch.setattr(pipeline, "generate_answer", fake_generate_answer)
    monkeypatch.setattr(pipeline, "log_query", fake_log_query)

    return SimpleNamespace(calls=calls, state=state)


def test_greeting_skips_retrieval_and_llm(fakes):
    result = pipeline.answer_question("hello")

    assert "Hello" in result["answer"]
    assert result["sources"] == []
    assert fakes.calls["search"] == 0
    assert fakes.calls["llm"] == 0


def test_out_of_scope_skips_retrieval_and_llm(fakes):
    result = pipeline.answer_question("what is the weather today")

    assert result["sources"] == []
    assert fakes.calls["search"] == 0
    assert fakes.calls["llm"] == 0


def test_abstains_when_nothing_relevant_is_found(fakes):
    fakes.state["reranked"] = []

    result = pipeline.answer_question("What is the stock option policy?")

    assert "don't have enough information" in result["answer"]
    assert result["sources"] == []
    assert fakes.calls["llm"] == 0           # LLM must NOT be called
    assert fakes.calls["logs"][0]["abstained"] is True


def test_abstains_when_all_rerank_scores_are_not_positive(fakes):
    fakes.state["reranked"] = [(make_chunk("unrelated text"), -3.2)]

    result = pipeline.answer_question("What is the stock option policy?")

    assert "don't have enough information" in result["answer"]
    assert fakes.calls["llm"] == 0


def test_successful_answer_has_citations_and_sources(fakes):
    fakes.state["reranked"] = [
        (make_chunk("Remote work is allowed three days per week.", page=2), 8.5),
        (make_chunk("Manager approval is required.", page=3), 4.1),
    ]

    result = pipeline.answer_question(
        "How many days can I work remotely?",
        department="general",
        access_level="employee",
    )

    assert result["answer"].startswith("Employees may work remotely")
    assert [s["citation"] for s in result["sources"]] == ["[1]", "[2]"]
    assert result["sources"][0]["page"] == 2
    assert result["sources"][0]["score"] == 8.5
    assert len(result["retrieved_contexts"]) == 2

    # the context given to the LLM contains the citation ids and the text
    context = fakes.calls["context"]
    assert "[1]" in context and "[2]" in context
    assert "Remote work is allowed three days per week." in context


def test_successful_answer_is_logged_as_not_abstained(fakes):
    fakes.state["reranked"] = [(make_chunk("Some policy text."), 5.0)]

    pipeline.answer_question("What is the leave policy?", department="hr")

    log = fakes.calls["logs"][0]
    assert log["abstained"] is False
    assert log["department"] == "hr"
    assert log["latency_ms"] >= 0

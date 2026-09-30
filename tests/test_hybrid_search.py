from types import SimpleNamespace

from app.rag import hybrid_search
from app.rag.hybrid_search import bm25_search, reciprocal_rank_fusion


def make_chunk(chunk_id, content, department="general", access_level="employee"):
    return SimpleNamespace(
        id=chunk_id,
        content=content,
        department=department,
        access_level=access_level,
    )


# ---------- Reciprocal Rank Fusion ----------

def test_rrf_puts_chunk_found_by_both_searches_first():
    a, b, c = make_chunk(1, "a"), make_chunk(2, "b"), make_chunk(3, "c")

    vector_results = [a, b]          # a is best for vector search
    bm25_results = [(c, 9.0), (b, 5.0)]  # c is best for BM25, b is also here

    ranked = reciprocal_rank_fusion(vector_results, bm25_results)

    # b appears in both lists, so it gets points twice and wins
    assert ranked[0].id == 2
    assert {chunk.id for chunk in ranked} == {1, 2, 3}


def test_rrf_has_no_duplicates():
    a = make_chunk(1, "a")
    ranked = reciprocal_rank_fusion([a], [(a, 1.0)])
    assert len(ranked) == 1


def test_rrf_handles_empty_inputs():
    assert reciprocal_rank_fusion([], []) == []


def test_rrf_with_only_vector_results_keeps_order():
    a, b = make_chunk(1, "a"), make_chunk(2, "b")
    ranked = reciprocal_rank_fusion([a, b], [])
    assert [chunk.id for chunk in ranked] == [1, 2]


# ---------- BM25 keyword search (database is faked) ----------

def test_bm25_ranks_chunk_with_matching_words_first(monkeypatch):
    chunks = [
        make_chunk(1, "office parking rules and visitor badges"),
        make_chunk(2, "employees may work remotely three days per week"),
        make_chunk(3, "expense reimbursement and travel booking process"),
    ]
    monkeypatch.setattr(hybrid_search, "get_all_documents", lambda: chunks)

    results = bm25_search("work remotely", k=3)

    assert results[0][0].id == 2


def test_bm25_respects_k(monkeypatch):
    chunks = [make_chunk(i, f"policy document number {i}") for i in range(1, 6)]
    monkeypatch.setattr(hybrid_search, "get_all_documents", lambda: chunks)

    assert len(bm25_search("policy", k=2)) == 2


def test_bm25_filters_by_department(monkeypatch):
    chunks = [
        make_chunk(1, "remote work policy", department="general"),
        make_chunk(2, "remote work rules for hr staff", department="hr"),
        make_chunk(3, "security password rules", department="security"),
    ]
    monkeypatch.setattr(hybrid_search, "get_all_documents", lambda: chunks)

    results = bm25_search("remote work", k=5, department="hr")

    assert [doc.id for doc, _ in results] == [2]


def test_bm25_returns_empty_list_when_no_documents(monkeypatch):
    monkeypatch.setattr(hybrid_search, "get_all_documents", lambda: [])
    assert bm25_search("anything") == []

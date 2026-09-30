from types import SimpleNamespace

from app.rag import reranker


class FakeCrossEncoder:
    """Pretends to be the real model: longer text gets a higher score."""

    def predict(self, pairs, batch_size=4):
        return [len(text) for _, text in pairs]


def make_doc(content):
    return SimpleNamespace(content=content)


def test_rerank_sorts_by_score_highest_first(monkeypatch):
    monkeypatch.setattr(reranker, "get_reranker", lambda: FakeCrossEncoder())
    docs = [make_doc("short"), make_doc("a much longer passage"), make_doc("medium one")]

    ranked = reranker.rerank_documents("query", docs, top_k=3)

    assert [doc.content for doc, _ in ranked] == [
        "a much longer passage",
        "medium one",
        "short",
    ]


def test_rerank_respects_top_k(monkeypatch):
    monkeypatch.setattr(reranker, "get_reranker", lambda: FakeCrossEncoder())
    docs = [make_doc("a" * n) for n in range(1, 8)]

    assert len(reranker.rerank_documents("query", docs, top_k=3)) == 3


def test_rerank_empty_list_does_not_load_the_model(monkeypatch):
    def should_not_be_called():
        raise AssertionError("model should not load for empty input")

    monkeypatch.setattr(reranker, "get_reranker", should_not_be_called)

    assert reranker.rerank_documents("query", []) == []

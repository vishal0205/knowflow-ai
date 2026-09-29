from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_reranker = None


def get_reranker():
    global _reranker

    if _reranker is None:
        _reranker = CrossEncoder(
            MODEL_NAME,
            device="cpu",
        )

    return _reranker


def rerank_documents(query: str, documents, top_k: int = 5):
    if not documents:
        return []

    reranker = get_reranker()

    pairs = [(query, document.content) for document in documents]

    scores = reranker.predict(
        pairs,
        batch_size=4,
    )

    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True,
    )

    return ranked[:top_k]
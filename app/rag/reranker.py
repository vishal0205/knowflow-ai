from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

reranker = CrossEncoder(MODEL_NAME)


def rerank_documents(query: str, documents, top_k: int = 5):
    """
    Rerank retrieved documents using a cross-encoder.
    """

    if not documents:
        return []

    pairs = [
        (query, document.content)
        for document in documents
    ]

    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True,
    )

    return ranked[:top_k]
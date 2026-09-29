from app.rag.retriever import search_documents
from app.rag.hybrid_search import (
    bm25_search,
    reciprocal_rank_fusion,
)
from app.rag.reranker import rerank_documents


query = "How many days can employees work remotely?"

# Step 1: Vector retrieval
vector_results = search_documents(query, k=10)

# Step 2: BM25
bm25_results = bm25_search(
    query,
    k=10,
)

# Step 3: RRF
hybrid_results = reciprocal_rank_fusion(
    vector_results,
    bm25_results,
)
# Step 4: Reranking
reranked_results = rerank_documents(
    query,
    hybrid_results,
    top_k=5,
)


print(f"\nQuery: {query}\n")

for i, (doc, score) in enumerate(
    reranked_results,
    start=1,
):
    print("=" * 70)
    print(f"RERANKED RESULT {i}")
    print("=" * 70)

    print("Reranker score:", float(score))
    print("Source:", doc.source)
    print("Page:", doc.page)

    print("\nContent:")
    print(doc.content)

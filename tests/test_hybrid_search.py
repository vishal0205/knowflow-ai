from app.rag.retriever import search_documents
from app.rag.hybrid_search import (
    bm25_search,
    reciprocal_rank_fusion,
)

query = "How many days can employees work remotely?"

# Vector retrieval
vector_results = search_documents(query, k=10)

# BM25 retrieval
bm25_results = bm25_search(
    query,
    k=10,
)

# Combine rankings
final_results = reciprocal_rank_fusion(
    vector_results,
    bm25_results,
)

print(f"\nQuery: {query}\n")

for i, doc in enumerate(final_results, start=1):
    print("=" * 70)
    print(f"RESULT {i}")
    print("=" * 70)
    print("Source:", doc.source)
    print("Page:", doc.page)
    print("Content:")
    print(doc.content)
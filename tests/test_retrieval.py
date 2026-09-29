from app.rag.retriever import search_documents


query = "How many days can employees work remotely?"

results = search_documents(query, k=3)

print(f"\nQuery: {query}")
print(f"Results: {len(results)}\n")

for i, result in enumerate(results, start=1):
    print("=" * 70)
    print(f"RESULT {i}")
    print("=" * 70)
    print("Source:", result.source)
    print("Page:", result.page)
    print("Content:")
    print(result.content)
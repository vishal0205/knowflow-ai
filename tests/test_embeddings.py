from app.rag.embeddings import get_embedding_model


embedding_model = get_embedding_model()


text = "Employees may work remotely three days per week."


vector = embedding_model.embed_query(text)


print("Embedding dimensions:", len(vector))

print("\nFirst 10 values:")
print(vector[:10])
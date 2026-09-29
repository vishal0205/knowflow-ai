from app.rag.ingestion import load_and_split_pdf


PDF_PATH = "data/documents/employee_handbook.pdf"


chunks = load_and_split_pdf(PDF_PATH)

print(f"\nTotal chunks: {len(chunks)}\n")


for index, chunk in enumerate(chunks, start=1):

    print("=" * 70)
    print(f"CHUNK {index}")
    print("=" * 70)

    print("\nCONTENT:")
    print(chunk.page_content)

    print("\nMETADATA:")
    print(chunk.metadata)
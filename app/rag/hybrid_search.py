from rank_bm25 import BM25Okapi
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import engine
from app.db.models import Document, DocumentChunk
from app.rag.retriever import search_documents


def tokenize(text: str):
    return text.lower().split()


def get_all_documents():
    with Session(engine) as session:
        stmt = (
            select(DocumentChunk)
            .join(
                Document,
                DocumentChunk.document_id == Document.id,
            )
            .where(Document.status == "active")
        )

        return session.execute(stmt).scalars().all()

def bm25_search(
    query: str,
    k: int = 10,
    department: str | None = None,
    access_level: str | None = None,
):
    documents = get_all_documents()

    if department:
        documents = [
            doc for doc in documents
            if doc.department == department
        ]

    if access_level:
        documents = [
            doc for doc in documents
            if doc.access_level == access_level
        ]

    if not documents:
        return []

    corpus = [tokenize(document.content) for document in documents]
    bm25 = BM25Okapi(corpus)

    query_tokens = tokenize(query)
    scores = bm25.get_scores(query_tokens)

    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:k]

def reciprocal_rank_fusion(
    vector_results,
    bm25_results,
    k: int = 60,
):
    scores = {}
    documents = {}

    for rank, doc in enumerate(
        vector_results,
        start=1,
    ):
        doc_id = doc.id

        documents[doc_id] = doc

        scores[doc_id] = (
            scores.get(doc_id, 0)
            + 1 / (k + rank)
        )

    for rank, (doc, _) in enumerate(
        bm25_results,
        start=1,
    ):
        doc_id = doc.id

        documents[doc_id] = doc

        scores[doc_id] = (
            scores.get(doc_id, 0)
            + 1 / (k + rank)
        )

    ranked = sorted(
        documents.values(),
        key=lambda doc: scores[doc.id],
        reverse=True,
    )

    return ranked

def hybrid_search(
    query: str,
    k: int = 10,
    department: str | None = None,
    access_level: str | None = None,
):
    vector_results = search_documents(
        query,
        k=k,
        department=department,
        access_level=access_level,
    )

    bm25_results = bm25_search(
        query,
        k=k,
        department=department,
        access_level=access_level,
    )

    return reciprocal_rank_fusion(
        vector_results,
        bm25_results,
    )
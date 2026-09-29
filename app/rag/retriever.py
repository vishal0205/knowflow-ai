from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import engine
from app.db.models import Document, DocumentChunk
from app.rag.embeddings import get_embedding_model

def search_documents(
    query: str,
    k: int = 5,
    department: str | None = None,
    access_level: str | None = None,
):
    embedding_model = get_embedding_model()
    query_embedding = embedding_model.embed_query(query)

    with Session(engine) as session:
        stmt = (
            select(DocumentChunk)
            .join(
                Document,
                DocumentChunk.document_id == Document.id,
            )
            .where(Document.status == "active")
        )

        if department:
            stmt = stmt.where(DocumentChunk.department == department)

        if access_level:
            stmt = stmt.where(DocumentChunk.access_level == access_level)

        stmt = (
            stmt
            .order_by(
                DocumentChunk.embedding.cosine_distance(query_embedding)
            )
            .limit(k)
        )

        results = session.execute(stmt).scalars().all()

    return results
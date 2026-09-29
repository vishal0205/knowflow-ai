from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import engine
from app.db.models import Document


def create_new_version(document_id: str) -> Document:
    with Session(engine) as session:
        current = session.execute(
            select(Document)
            .where(Document.document_id == document_id)
            .where(Document.status == "active")
            .order_by(Document.version.desc())
        ).scalar_one_or_none()

        if not current:
            raise ValueError(
                f"No active document found for: {document_id}"
            )

        current.status = "archived"

        new_version = Document(
            document_id=current.document_id,
            filename=current.filename,
            version=current.version + 1,
            effective_date=None,
            status="active",
            department=current.department,
            access_level=current.access_level,
        )

        session.add(new_version)
        session.commit()
        session.refresh(new_version)

        return new_version
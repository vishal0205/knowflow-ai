from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.database import engine
from app.db.models import Document, DocumentChunk
from app.rag.embeddings import get_embedding_model
from app.rag.ingestion import load_and_split_pdf
import hashlib
from pathlib import Path

from sqlalchemy import delete, select

def calculate_file_hash(file_path: str) -> str:
    hasher = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            hasher.update(chunk)

    return hasher.hexdigest()

def get_document_permissions(file_path: str):
    filename = Path(file_path).name

    permissions = {
        "remote_work_policy.pdf": ("general", "employee"),
        "security_policy.pdf": ("security", "employee"),
        "leave_policy.pdf": ("hr", "employee"),
        "benefits_policy.pdf": ("hr", "employee"),
        "employee_handbook.pdf": ("general", "employee"),
        "manual.pdf": ("general", "employee"),
    }

    return permissions.get(filename, ("general", "employee"))


def get_or_create_document(
    session: Session,
    file_path: str,
) -> Document:
    filename = Path(file_path).name

    document = session.execute(
        select(Document).where(Document.filename == filename)
    ).scalar_one_or_none()

    if document:
        return document

    department, access_level = get_document_permissions(file_path)

    document_id = Path(filename).stem.replace("_", "-")

    document = Document(
        document_id=document_id,
        filename=filename,
        version=1,
        status="active",
        department=department,
        access_level=access_level,
    )

    session.add(document)
    session.flush()

    return document

def index_pdf(file_path: str):
    file_hash = calculate_file_hash(file_path)
    filename = Path(file_path).name
    source = str(Path(file_path))

    with Session(engine) as session:
        active_document = session.execute(
            select(Document)
            .where(Document.filename == filename)
            .where(Document.status == "active")
            .order_by(Document.version.desc())
        ).scalar_one_or_none()

        # Same content already indexed
        if active_document and active_document.content_hash == file_hash:
            print(
                f"Skipped {filename}: "
                f"content unchanged (version {active_document.version})"
            )
            return

        department, access_level = get_document_permissions(file_path)

        # New document
        if not active_document:
            document_id = Path(filename).stem.replace("_", "-")

            document = Document(
                document_id=document_id,
                filename=filename,
                version=1,
                status="active",
                department=department,
                access_level=access_level,
                content_hash=file_hash,
            )

        # Existing document changed → create new version
        else:
            active_document.status = "archived"

            document = Document(
                document_id=active_document.document_id,
                filename=filename,
                version=active_document.version + 1,
                status="active",
                department=department,
                access_level=access_level,
                content_hash=file_hash,
            )

        session.add(document)
        session.flush()

        # Parse and chunk the PDF
        documents = load_and_split_pdf(file_path)

        embedding_model = get_embedding_model()

        for index, document_chunk in enumerate(documents):
            embedding = embedding_model.embed_query(
                document_chunk.page_content
            )

            page = document_chunk.metadata.get("page")

            chunk_id = (
                f"{document.document_id}_"
                f"v{document.version}_"
                f"{page}_{index}"
            )

            record = DocumentChunk(
                document_id=document.id,
                content=document_chunk.page_content,
                source=source,
                page=page,
                chunk_id=chunk_id,
                department=department,
                access_level=access_level,
                embedding=embedding,
            )

            session.add(record)

        session.commit()

        print(
            f"Indexed {len(documents)} chunks from {filename} "
            f"[document_id={document.document_id}, "
            f"version={document.version}, "
            f"department={department}, "
            f"access={access_level}]"
        )




        
def index_directory(directory: str):
    directory_path = Path(directory)
    pdf_files = sorted(directory_path.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found.")
        return

    for pdf_file in pdf_files:
        index_pdf(str(pdf_file))

    print(f"\nFinished indexing {len(pdf_files)} documents.")
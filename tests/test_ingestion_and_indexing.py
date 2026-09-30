import hashlib

import pytest

from app.rag.ingestion import load_and_split_pdf
from app.rag.vector_store import calculate_file_hash, get_document_permissions


def test_loading_a_missing_pdf_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_and_split_pdf("data/documents/does_not_exist.pdf")


def test_file_hash_matches_sha256(tmp_path):
    file = tmp_path / "policy.pdf"
    file.write_bytes(b"same content")

    assert calculate_file_hash(str(file)) == hashlib.sha256(b"same content").hexdigest()


def test_file_hash_changes_when_content_changes(tmp_path):
    file = tmp_path / "policy.pdf"

    file.write_bytes(b"version one")
    first = calculate_file_hash(str(file))

    file.write_bytes(b"version two")
    second = calculate_file_hash(str(file))

    assert first != second


def test_known_document_gets_its_department():
    assert get_document_permissions("data/documents/leave_policy.pdf") == (
        "hr",
        "employee",
    )


def test_unknown_document_gets_default_permissions():
    assert get_document_permissions("data/documents/new_file.pdf") == (
        "general",
        "employee",
    )

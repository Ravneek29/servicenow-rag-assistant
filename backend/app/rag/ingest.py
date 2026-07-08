"""Document loading, chunking, and indexing."""

from pathlib import Path

from langchain_community.document_loaders import (
    BSHTMLLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app import config
from app.rag.store import delete_document, get_vectorstore


def load_file(path: Path) -> list[Document]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(path)).load()
    if suffix in (".html", ".htm"):
        return BSHTMLLoader(str(path)).load()
    return TextLoader(str(path), encoding="utf-8").load()


def ingest_file(path: Path, source_name: str) -> dict:
    """Chunk and index one file. Re-uploading a file replaces its chunks.

    Returns {"chunks": int, "chars": int, "warning": str | None}.
    """
    docs = load_file(path)
    total_chars = sum(len(d.page_content) for d in docs)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    if not chunks:
        return {"chunks": 0, "chars": 0, "warning": None}

    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = source_name
        chunk.metadata["chunk"] = i
        # PDF loaders set a 0-indexed page; normalize to 1-indexed for citations
        if "page" in chunk.metadata:
            chunk.metadata["page"] = int(chunk.metadata["page"]) + 1

    delete_document(source_name)  # idempotent re-upload
    get_vectorstore().add_documents(chunks)

    warning = None
    file_size = path.stat().st_size
    # Web-save PDFs of JS-heavy pages often contain almost no text layer;
    # flag it so the user knows the content didn't actually make it in.
    if path.suffix.lower() == ".pdf" and (
        total_chars < 2000 or total_chars < file_size * 0.01
    ):
        warning = (
            "Very little text could be extracted from this PDF — it may be "
            "image-based or a browser web-save. For docs.servicenow.com "
            "pages, use Print (Cmd+P) → Save as PDF, or save the page as "
            "HTML and upload that instead."
        )

    return {"chunks": len(chunks), "chars": total_chars, "warning": warning}

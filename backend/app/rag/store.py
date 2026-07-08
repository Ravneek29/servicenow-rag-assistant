"""ChromaDB vector store shared across the app."""

from functools import lru_cache

from langchain_chroma import Chroma

from app import config
from app.rag.embeddings import LocalEmbeddings


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    return Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=LocalEmbeddings(),
        persist_directory=config.CHROMA_DIR,
    )


def list_documents() -> list[dict]:
    """Return each ingested document with its chunk count."""
    store = get_vectorstore()
    records = store._collection.get(include=["metadatas"])
    counts: dict[str, int] = {}
    for meta in records["metadatas"]:
        source = meta.get("source", "unknown")
        counts[source] = counts.get(source, 0) + 1
    return [
        {"name": name, "chunks": count}
        for name, count in sorted(counts.items())
    ]


def delete_document(source: str) -> int:
    """Remove all chunks belonging to one uploaded document."""
    store = get_vectorstore()
    records = store._collection.get(where={"source": source})
    ids = records["ids"]
    if ids:
        store._collection.delete(ids=ids)
    return len(ids)

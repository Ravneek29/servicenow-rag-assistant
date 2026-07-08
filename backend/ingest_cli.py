"""Bulk-ingest large documents from the command line.

The upload API is capped (local CPU embeddings make huge files impractical
inside one HTTP request); this script handles big PDF books instead, adding
chunks in batches with progress output.

Usage:
    python ingest_cli.py /path/to/big-book.pdf [--name "friendly-name.pdf"]
"""

import argparse
import sys
import time
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app import config
from app.rag.ingest import load_file
from app.rag.store import delete_document, get_vectorstore

BATCH_SIZE = 200


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--name", help="Source name shown in citations")
    args = parser.parse_args()

    if not args.path.exists():
        print(f"File not found: {args.path}")
        return 1
    source_name = args.name or args.path.name

    print(f"Loading {args.path.name} …")
    start = time.time()
    docs = load_file(args.path)
    print(f"  parsed {len(docs)} pages/sections in {time.time() - start:.0f}s")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"  split into {len(chunks)} chunks")

    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = source_name
        chunk.metadata["chunk"] = i
        if "page" in chunk.metadata:
            chunk.metadata["page"] = int(chunk.metadata["page"]) + 1

    print("Removing any previous chunks for this source …")
    delete_document(source_name)

    store = get_vectorstore()
    embed_start = time.time()
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        store.add_documents(batch)
        done = min(i + BATCH_SIZE, len(chunks))
        elapsed = time.time() - embed_start
        rate = done / elapsed if elapsed else 0
        eta = (len(chunks) - done) / rate if rate else 0
        print(
            f"  indexed {done}/{len(chunks)} chunks "
            f"({rate:.0f}/s, ~{eta:.0f}s remaining)",
            flush=True,
        )

    print(f"Done: {len(chunks)} chunks in {time.time() - start:.0f}s total")
    return 0


if __name__ == "__main__":
    sys.exit(main())

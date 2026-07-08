from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app import config
from app.rag.ingest import ingest_file
from app.rag.store import delete_document, list_documents

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("")
def get_documents():
    return {"documents": list_documents()}


@router.post("")
async def upload_document(file: UploadFile):
    name = Path(file.filename or "").name
    if not name:
        raise HTTPException(400, "Missing filename")
    suffix = Path(name).suffix.lower()
    if suffix not in config.ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(config.ALLOWED_EXTENSIONS))
        raise HTTPException(400, f"Unsupported file type '{suffix}'. Allowed: {allowed}")

    content = await file.read()
    max_bytes = config.MAX_UPLOAD_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            413,
            f"'{name}' is {len(content) / 1024 / 1024:.0f} MB — the limit is "
            f"{config.MAX_UPLOAD_MB} MB. Large PDF books take too long to "
            "index locally; upload individual chapters or saved pages instead.",
        )

    upload_dir = Path(config.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / name
    dest.write_bytes(content)

    try:
        result = ingest_file(dest, name)
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(422, f"Could not parse '{name}': {exc}")

    if result["chunks"] == 0:
        raise HTTPException(422, f"No text content found in '{name}'")
    return {"name": name, **result}


@router.delete("/{name}")
def remove_document(name: str):
    deleted = delete_document(Path(name).name)
    if deleted == 0:
        raise HTTPException(404, f"Document '{name}' not found")
    (Path(config.UPLOAD_DIR) / Path(name).name).unlink(missing_ok=True)
    return {"name": name, "deleted_chunks": deleted}


@router.post("/load-samples")
def load_samples():
    """Index the bundled sample ServiceNow docs (demo convenience)."""
    sample_dir = Path(config.SAMPLE_DOCS_DIR)
    loaded = []
    for path in sorted(sample_dir.glob("*.md")):
        result = ingest_file(path, path.name)
        loaded.append({"name": path.name, "chunks": result["chunks"]})
    return {"documents": loaded}

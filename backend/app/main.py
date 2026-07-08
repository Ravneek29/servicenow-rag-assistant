from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.routers import chat, documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On ephemeral-disk hosts the index is wiped on every deploy; re-seed the
    # bundled sample docs so the demo is never empty.
    if config.SEED_SAMPLES_IF_EMPTY:
        from app.rag.ingest import ingest_file
        from app.rag.store import get_vectorstore

        if get_vectorstore()._collection.count() == 0:
            for path in sorted(Path(config.SAMPLE_DOCS_DIR).glob("*.md")):
                ingest_file(path, path.name)
    yield


app = FastAPI(
    title="ServiceNow RAG Knowledge Assistant",
    description=(
        "Upload ServiceNow documentation, ask questions in natural language, "
        "and get answers with citations. LangChain + ChromaDB + Claude."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

allowed_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
if config.FRONTEND_ORIGIN:
    allowed_origins.append(config.FRONTEND_ORIGIN.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}

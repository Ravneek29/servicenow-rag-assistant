from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import chat, documents

app = FastAPI(
    title="ServiceNow RAG Knowledge Assistant",
    description=(
        "Upload ServiceNow documentation, ask questions in natural language, "
        "and get answers with citations. LangChain + ChromaDB + Claude."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}

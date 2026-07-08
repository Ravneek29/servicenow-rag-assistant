import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-8")
CHROMA_DIR = os.getenv("CHROMA_DIR", str(BASE_DIR / "chroma_data"))
UPLOAD_DIR = str(BASE_DIR / "uploads")
SAMPLE_DOCS_DIR = str(BASE_DIR / "sample_docs")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
TOP_K = int(os.getenv("TOP_K", "5"))

# Chunks scoring below this relevance are discarded rather than sent to the
# LLM — weak matches add noise and tempt small models to answer from scraps.
MIN_RELEVANCE = float(os.getenv("MIN_RELEVANCE", "0.3"))

COLLECTION_NAME = "servicenow_docs"

# "auto"       — use the LLM, fall back to extractive passages if it fails
# "llm"        — LLM only; surface errors
# "extractive" — never call an LLM; return top passages (fully free)
ANSWER_MODE = os.getenv("ANSWER_MODE", "auto").lower()

# "anthropic" — Claude API (needs ANTHROPIC_API_KEY + credits)
# "ollama"    — local open-weights model via Ollama (free, runs on-device)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic").lower()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt", ".html", ".htm"}

# Local CPU embeddings make very large files impractical to index in one
# request; cap uploads so a huge PDF can't wedge the server.
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "25"))

# ServiceNow RAG Knowledge Assistant

A Retrieval-Augmented Generation (RAG) application that turns ServiceNow
documentation into a searchable, conversational knowledge base. Upload docs,
ask questions in natural language, and get grounded answers with inline,
clickable citations back to the exact source passages.

**Stack:** FastAPI · LangChain · ChromaDB · Claude (Anthropic) · React (Vite)

## How it works

```
                    ┌─────────────────────────────────────────────┐
                    │                  FastAPI                     │
  React UI ──────▶  │                                             │
                    │  Upload ──▶ LangChain loaders (PDF/MD/HTML) │
                    │             └─▶ RecursiveCharacterSplitter  │
                    │                 └─▶ ChromaDB (local ONNX    │
                    │                     MiniLM embeddings)      │
                    │                                             │
                    │  Ask ──▶ similarity search (top-k chunks)   │
                    │          └─▶ Claude w/ numbered excerpts    │
                    │              └─▶ answer + [n] citations     │
                    └─────────────────────────────────────────────┘
```

- **Ingestion** — documents are parsed with LangChain loaders, split into
  overlapping chunks, embedded locally (no embedding API key needed), and
  persisted in ChromaDB. Re-uploading a file replaces its chunks.
- **Retrieval** — questions are embedded and matched against the index;
  the top-k chunks are returned with relevance scores.
- **Generation** — Claude receives only the numbered excerpts and is
  instructed to cite every claim as `[n]` and to refuse rather than answer
  from general knowledge (grounding / hallucination control).
- **Citations** — the UI parses `[n]` markers into chips; clicking one shows
  the source document, page, relevance score, and passage snippet.

## Running locally

### 1. Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # add your ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev                # http://localhost:5173
```

### 3. Try it

Click **Load sample ServiceNow docs** (bundled docs covering Incident
Management, Change Management, and the CMDB), then ask:

- *How is incident priority calculated?*
- *What is the difference between a normal and a standard change?*
- *How does the IRE prevent duplicate CIs?*

Or upload your own exported ServiceNow documentation (PDF, Markdown, HTML,
or plain text).

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents` | Upload + index a document (multipart) |
| `GET` | `/api/documents` | List indexed documents with chunk counts |
| `DELETE` | `/api/documents/{name}` | Remove a document from the index |
| `POST` | `/api/documents/load-samples` | Index the bundled sample docs |
| `POST` | `/api/ask` | `{question, top_k?}` → `{answer, sources[]}` |
| `GET` | `/api/health` | Health check |

Interactive docs at `http://localhost:8000/docs` (Swagger UI).

## Design decisions

- **Local embeddings** (ChromaDB's ONNX MiniLM) keep the project a
  single-key setup and make ingestion free — only answer generation calls
  the Claude API.
- **Grounded prompting** — the model only sees retrieved excerpts and must
  cite them; if the excerpts don't cover the question it says so instead of
  hallucinating.
- **Idempotent ingestion** — re-uploading a document deletes its old chunks
  first, so the index never accumulates stale duplicates.
- **Chunking tuned for docs** — 1000 chars with 150 overlap, splitting on
  paragraphs before sentences, which keeps ServiceNow tables and lists
  intact within chunks.
- **Pluggable LLM provider** (`LLM_PROVIDER` env var) — `anthropic` uses the
  Claude API for the highest-quality synthesis; `ollama` runs a local
  open-weights model (e.g. Llama 3.2 via [Ollama](https://ollama.com)) so
  the entire stack works offline with zero API cost.
- **Graceful degradation** (`ANSWER_MODE` env var) — in `auto` mode the app
  uses the configured LLM and falls back to extractive search (top passages
  returned verbatim, still cited) if the LLM call fails, so the demo never
  breaks. `extractive` mode runs the whole app with no LLM at all.
- **Bulk ingestion CLI** (`python ingest_cli.py <file>`) — large PDF books
  (thousands of pages) are indexed in batches with progress output, instead
  of through the size-capped upload endpoint.

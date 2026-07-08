"""Local embeddings via ChromaDB's bundled ONNX MiniLM model.

Runs entirely on-device: no embedding API key required, which keeps the
project a single-key setup (Anthropic key for generation only).
"""

from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from langchain_core.embeddings import Embeddings


class LocalEmbeddings(Embeddings):
    def __init__(self) -> None:
        self._ef = DefaultEmbeddingFunction()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(x) for x in vec] for vec in self._ef(texts)]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

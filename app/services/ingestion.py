from __future__ import annotations

from pathlib import Path

from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStore


class IngestionService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        chunk_size: int = 150,
        chunk_overlap: int = 30,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def ingest_file(self, doc_path: Path) -> int:
        text = doc_path.read_text(encoding="utf-8")
        chunks = self.chunk_text(text)
        if not chunks:
            return 0

        ids: list[str] = []
        documents: list[str] = []
        embeddings: list[list[float]] = []
        metadatas: list[dict[str, str | int]] = []

        for idx, chunk in enumerate(chunks):
            ids.append(f"{doc_path.stem}:{idx}")
            documents.append(chunk)
            embeddings.append(self.embedding_service.embed_text(chunk))
            metadatas.append(
                {
                    "source": doc_path.name,
                    "chunk_index": idx,
                }
            )

        self.vector_store.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        return len(chunks)

    def chunk_text(self, text: str) -> list[str]:
        cleaned = text.strip()
        if not cleaned:
            return []

        chunks: list[str] = []
        start = 0
        text_length = len(cleaned)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk = cleaned[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= text_length:
                break
            start = max(end - self.chunk_overlap, start + 1)

        return chunks

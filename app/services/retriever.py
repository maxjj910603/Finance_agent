from __future__ import annotations

from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStore


class Retriever:
    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def retrieve(self, question: str, top_k: int = 3) -> list[dict]:
        query_embedding = self.embedding_service.embed_text(question)
        return self.vector_store.query(query_embedding=query_embedding, top_k=top_k)

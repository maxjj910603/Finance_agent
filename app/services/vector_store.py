from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb


class VectorStore:
    def __init__(self, persist_dir: Path, collection_name: str = "finance_policy") -> None:
        self.persist_dir = persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def upsert(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
    ) -> None:
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def query(self, query_embedding: list[float], top_k: int = 3) -> list[dict[str, Any]]:
        result = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)

        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        rows: list[dict[str, Any]] = []
        for idx, doc_id in enumerate(ids):
            rows.append(
                {
                    "id": doc_id,
                    "document": documents[idx],
                    "metadata": metadatas[idx],
                    "distance": distances[idx] if idx < len(distances) else None,
                }
            )
        return rows

    def count(self) -> int:
        return self.collection.count()

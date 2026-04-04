from __future__ import annotations

from app.schemas import EvidenceItem
from app.services.llm_client import LLMClient
from app.services.retriever import Retriever


class RAGSkill:
    def __init__(self, retriever: Retriever, llm_client: LLMClient) -> None:
        self.retriever = retriever
        self.llm_client = llm_client

    def run(self, question: str) -> tuple[str, list[EvidenceItem]]:
        hits = self.retriever.retrieve(question, top_k=3)
        if not hits:
            return "insufficient evidence", [
                EvidenceItem(type="rag", source="vector_store", detail="No relevant chunks retrieved."),
            ]

        context_chunks: list[str] = []
        evidence: list[EvidenceItem] = []
        for hit in hits:
            document = hit["document"]
            metadata = hit["metadata"] or {}
            source = metadata.get("source", "unknown_document")
            chunk_index = metadata.get("chunk_index", "unknown")
            distance = hit.get("distance")
            context_chunks.append(document)
            evidence.append(
                EvidenceItem(
                    type="rag",
                    source=str(source),
                    detail=f"chunk_index={chunk_index}; distance={distance}; snippet={document[:220]}",
                )
            )

        answer = self.llm_client.write_rag_answer(question, context_chunks)
        return answer, evidence

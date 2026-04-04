from __future__ import annotations

from app.schemas import EvidenceItem
from app.services.llm_client import LLMClient


class HybridSkill:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def run(
        self,
        question: str,
        sql_answer: str,
        rag_answer: str,
        sql_evidence: list[EvidenceItem],
        rag_evidence: list[EvidenceItem],
    ) -> tuple[str, list[EvidenceItem]]:
        draft_answer = (
            f"SQL facts: {sql_answer}\n"
            f"Policy context: {rag_answer}"
        )
        evidence = sql_evidence + rag_evidence
        evidence_lines = [f"{item.source}: {item.detail}" for item in evidence[:6]]
        final_answer = self.llm_client.write_answer(question, "hybrid", draft_answer, evidence_lines)
        return final_answer, evidence

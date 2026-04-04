from __future__ import annotations

import re

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
        skill_instructions: str,
    ) -> tuple[str, list[EvidenceItem]]:
        del question, skill_instructions

        sql_part = self._clean_answer(sql_answer)
        rag_part = self._clean_answer(rag_answer)

        parts: list[str] = []
        if sql_part:
            parts.append(sql_part)
        if rag_part and rag_part.lower() != "insufficient evidence":
            parts.append(rag_part)

        if not parts:
            parts.append("insufficient evidence")

        answer = "\n".join(parts)
        evidence = sql_evidence + rag_evidence
        return answer, evidence

    @staticmethod
    def _clean_answer(text: str) -> str:
        cleaned = text.strip()
        cleaned = re.sub(r"(?im)^sql sub-answer:\s*", "", cleaned)
        cleaned = re.sub(r"(?im)^policy sub-answer:\s*", "", cleaned)
        cleaned = re.sub(r"(?im)^資料庫結果：\s*", "", cleaned)
        cleaned = re.sub(r"(?im)^文件依據：\s*", "", cleaned)
        cleaned = re.sub(r"(?im)^write one combined user-facing answer.*$", "", cleaned)
        cleaned = re.sub(r"\n{2,}", "\n", cleaned).strip()
        return cleaned

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Optional

from app.schemas import RouterResult


class LLMClient:
    def __init__(self) -> None:
        self.host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        self.model = os.getenv("LLM_MODEL", "qwen2.5:7b-instruct")

    def classify_route(self, question: str) -> Optional[RouterResult]:
        system = (
            "You are a routing model for finance QA. "
            "Choose exactly one route: chat, sql, rag, or hybrid. "
            "Use chat for greetings or general conversation. "
            "Use sql for structured questions answerable from finance table data. "
            "Use rag for reimbursement, budget, policy, or regulation questions grounded in documents. "
            "Use hybrid only when both finance data and finance policy context are required. "
            "Return strict JSON only with keys route, reason, confidence."
        )
        user = (
            f"Question: {question}\n"
            "Output JSON format:\n"
            '{"route":"chat|sql|rag|hybrid","reason":"...","confidence":0.0}'
        )
        raw = self._call_ollama_text(system=system, user=user, max_output_tokens=120, temperature=0.0)
        return self._parse_route(raw)

    def chat_answer(self, question: str) -> str:
        system = (
            "You are a concise finance assistant. "
            "Reply in Traditional Chinese only. "
            "If the user is greeting you, greet them naturally. "
            "Do not mention routing, SQL, or documents unless the user asks about them."
        )
        user = f"User message: {question}"
        answer = self._call_ollama_text(system=system, user=user, max_output_tokens=160, temperature=0.3)
        if answer:
            return answer
        return "你好，我可以協助你處理財務資料與財務規範相關問題。"

    def generate_sql(self, question: str, db_schema: str) -> Optional[str]:
        system = (
            "You generate one read-only SQLite query for finance analytics. "
            "Return SQL only, no markdown, no explanation. "
            "Use only the provided schema. "
            "Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, or multi-statement SQL."
        )
        user = (
            f"Schema: {db_schema}\n"
            f"Question: {question}\n"
            "Return exactly one SELECT SQL statement."
        )
        raw = self._call_ollama_text(system=system, user=user, max_output_tokens=180, temperature=0.0)
        if not raw:
            return None
        return self._strip_code_fence(raw)

    def write_answer(
        self,
        question: str,
        route: str,
        draft_answer: str,
        evidence_lines: list[str],
    ) -> str:
        system = (
            "You are a finance QA assistant. "
            "Rewrite draft answers into concise, clear, professional Traditional Chinese. "
            "Stay grounded to provided evidence. "
            "Do not invent facts. "
            "Return plain text only."
        )
        user = (
            f"Question: {question}\n"
            f"Route: {route}\n"
            f"Draft answer: {draft_answer}\n"
            f"Evidence:\n- " + "\n- ".join(evidence_lines)
        )
        refined = self._call_ollama_text(system=system, user=user, max_output_tokens=220, temperature=0.2)
        if refined:
            return refined

        if route == "sql":
            return f"根據財務資料：{draft_answer}"
        if route == "rag":
            return f"根據財務規範文件：{draft_answer}"
        if route == "chat":
            return draft_answer
        return f"綜合財務資料與規範後：{draft_answer}"

    def write_rag_answer(self, question: str, context_chunks: list[str]) -> str:
        system = (
            "You are a finance policy QA assistant. "
            "Answer in concise, professional Traditional Chinese. "
            "Use only the provided retrieved document context. "
            "If the context is insufficient, say insufficient evidence. "
            "Return plain text only."
        )
        user = (
            f"Question: {question}\n"
            "Retrieved context:\n- " + "\n- ".join(context_chunks)
        )
        answer = self._call_ollama_text(system=system, user=user, max_output_tokens=220, temperature=0.2)
        if answer:
            return answer
        return "insufficient evidence"

    def _call_ollama_text(
        self,
        system: str,
        user: str,
        max_output_tokens: int,
        temperature: float,
    ) -> Optional[str]:
        payload = {
            "model": self.model,
            "system": system,
            "prompt": user,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_output_tokens,
            },
        }

        req = urllib.request.Request(
            url=f"{self.host}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
            return None

        text = data.get("response")
        if isinstance(text, str) and text.strip():
            return text.strip()
        return None

    @staticmethod
    def _parse_route(raw: str | None) -> Optional[RouterResult]:
        if not raw:
            return None

        data = None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}")
            if start == -1 or end == -1 or end <= start:
                return None
            try:
                data = json.loads(raw[start : end + 1])
            except json.JSONDecodeError:
                return None

        route = data.get("route")
        if route not in {"chat", "sql", "rag", "hybrid"}:
            return None

        reason = str(data.get("reason", "llm route"))
        confidence = float(data.get("confidence", 0.0))
        return RouterResult(route=route, reason=reason, confidence=confidence)

    @staticmethod
    def _strip_code_fence(text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if len(lines) >= 2 and lines[-1].strip() == "```":
                return "\n".join(lines[1:-1]).strip()
        return cleaned

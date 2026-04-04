from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Optional

from app.schemas import RouterResult


class LLMClient:
    def __init__(self) -> None:
        self.host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        self.model = os.getenv("LLM_MODEL", "qwen2.5:7b-instruct")

    def classify_skill(self, question: str, skill_summaries: list[dict[str, str]]) -> Optional[RouterResult]:
        skills_text = "\n".join(
            [f"- {item['name']}: {item['description']}" for item in skill_summaries]
        )
        system = (
            "You are a finance skill router. "
            "Read the user question and choose exactly one skill from the provided skill list. "
            "Return strict JSON only with keys route, reason, confidence. "
            "The route value must exactly match one provided skill name."
        )
        user = (
            f"Question: {question}\n"
            f"Available skills:\n{skills_text}\n"
            'Output JSON format: {"route":"skill-name","reason":"...","confidence":0.0}'
        )
        raw = self._call_ollama_text(system=system, user=user, max_output_tokens=180, temperature=0.0)
        return self._parse_route(raw)

    def chat_answer(self, question: str, skill_instructions: str) -> str:
        system = (
            "You are a concise finance assistant. "
            "Reply in Traditional Chinese only. "
            "Follow the provided skill instructions. "
            "Return only the final reply. "
            "Do not mention routing or internal tools unless asked."
        )
        user = f"Skill instructions:\n{skill_instructions}\n\nUser message: {question}"
        answer = self._call_ollama_text(system=system, user=user, max_output_tokens=160, temperature=0.3)
        if answer:
            return self._cleanup_answer(answer)
        return "你好，我可以協助你處理財務資料與財務規範相關問題。"

    def generate_sql(self, question: str, db_schema: str, skill_instructions: str) -> Optional[str]:
        system = (
            "You generate one read-only SQLite query for finance analytics. "
            "Follow the provided skill instructions. "
            "Return SQL only, no markdown, no explanation. "
            "Use only the provided schema. "
            "Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, or multi-statement SQL."
        )
        user = (
            f"Skill instructions:\n{skill_instructions}\n\n"
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
        skill_instructions: str,
    ) -> str:
        system = (
            "You are a finance QA assistant. "
            "Write a concise, clear, professional Traditional Chinese answer. "
            "Follow the provided skill instructions. "
            "Stay grounded to the provided evidence. "
            "Do not invent facts. "
            "Do not output field labels such as sql, rows, summary, evidence, answer, route, citations, or markdown fences. "
            "Return only the final user-facing answer."
        )
        user = (
            f"Skill instructions:\n{skill_instructions}\n\n"
            f"Question: {question}\n"
            f"Route: {route}\n"
            f"Draft answer: {draft_answer}\n"
            f"Evidence:\n- " + "\n- ".join(evidence_lines)
        )
        refined = self._call_ollama_text(system=system, user=user, max_output_tokens=220, temperature=0.2)
        if refined:
            return self._cleanup_answer(refined)

        if route == "sql":
            return f"根據財務資料：{draft_answer}"
        if route == "rag":
            return f"根據財務規範文件：{draft_answer}"
        if route == "chat":
            return draft_answer
        return f"綜合財務資料與規範後：{draft_answer}"

    def write_rag_answer(self, question: str, context_chunks: list[str], skill_instructions: str) -> str:
        system = (
            "You are a finance policy QA assistant. "
            "Answer in concise, professional Traditional Chinese. "
            "Follow the provided skill instructions. "
            "Use only the provided retrieved document context. "
            "If the context is insufficient, say insufficient evidence. "
            "Do not output labels such as answer, citations, or evidence. "
            "Return only the final answer."
        )
        user = (
            f"Skill instructions:\n{skill_instructions}\n\n"
            f"Question: {question}\n"
            "Retrieved context:\n- " + "\n- ".join(context_chunks)
        )
        answer = self._call_ollama_text(system=system, user=user, max_output_tokens=220, temperature=0.2)
        if answer:
            return self._cleanup_answer(answer)
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
        if not isinstance(route, str):
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

    @staticmethod
    def _cleanup_answer(text: str) -> str:
        cleaned = text.strip()
        cleaned = cleaned.replace("```sql", "").replace("```", "").strip()

        label_patterns = [
            r"(?im)^answer:\s*",
            r"(?im)^sql:\s*",
            r"(?im)^rows:\s*",
            r"(?im)^summary:\s*",
            r"(?im)^evidence:\s*",
            r"(?im)^citations:\s*",
            r"(?im)^回答：\s*",
            r"(?im)^答案：\s*",
            r"(?im)^證據：\s*",
            r"(?im)^引用：\s*",
        ]
        for pattern in label_patterns:
            cleaned = re.sub(pattern, "", cleaned)

        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
        return cleaned

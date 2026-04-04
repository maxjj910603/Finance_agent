from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Optional

from app.schemas import HybridQuestionParts, RouterResult


class LLMClient:
    def __init__(self) -> None:
        self.host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        self.model = os.getenv("LLM_MODEL", "qwen2.5:7b-instruct")

    def classify_route(
        self,
        question: str,
        route_summaries: list[dict[str, str]],
    ) -> Optional[RouterResult]:
        routes_text = "\n".join(
            [f"- {item['route']}: {item['description']}" for item in route_summaries]
        )
        system = (
            "You are a finance route selector. "
            "Choose exactly one route from chat, sql, rag, hybrid. "
            "Return strict JSON only with keys route, reason, confidence. "
            "The route value must be exactly one of: chat, sql, rag, hybrid. "
            "If the question asks about reimbursement rules, payment applications, approval thresholds, sign-off, required attachments, policy, procedures, or whether something is allowed, prefer rag. "
            "If the question asks about revenue, expense, profit, averages, totals, rankings, months, or values from structured finance data, prefer sql. "
            "If the question needs both structured metrics and policy rules, always choose hybrid. "
            "If one part of the question asks for a database value and another part asks about approval requirements, reimbursement rules, procurement rules, sign-off, or policy interpretation, choose hybrid. "
            "Do not choose sql when any material part of the question requires document-grounded policy evidence. "
            "Examples: "
            "chat example: 'hello' => chat. "
            "chat example: '你可以幫我做什麼？' => chat. "
            "sql example: '2025 年 6 月淨利是多少？' => sql. "
            "sql example: 'Which month has the highest net profit?' => sql. "
            "rag example: '報銷申請原則上應在支出發生後多久內提出？' => rag. "
            "rag example: '國外出差每日膳雜費補助是多少？' => rag. "
            "hybrid example: '2025 年 6 月淨利是多少？如果當月有一筆 60,000 元的採購，依規範需要哪些人核准？' => hybrid. "
            "hybrid example: '哪一個月份淨利最高，且若要追加 20% 預算需要什麼程序？' => hybrid. "
            "Choose chat only for greetings, casual conversation, or non-finance small talk."
        )
        user = (
            f"Question: {question}\n"
            f"Available routes:\n{routes_text}\n"
            'Output JSON format: {"route":"chat|sql|rag|hybrid","reason":"short reason","confidence":0.0}'
        )
        raw = self._call_ollama_text(system=system, user=user, max_output_tokens=120, temperature=0.0)
        return self._parse_route(raw)

    def chat_answer(self, question: str, skill_instructions: str) -> str:
        system = (
            "You are a concise finance assistant. "
            "Reply in Traditional Chinese used in Taiwan only. "
            "Never use Simplified Chinese characters. "
            "Follow the provided skill instructions. "
            "Return only the final reply. "
            "Do not mention routing or internal tools unless asked."
        )
        user = f"Skill instructions:\n{skill_instructions}\n\nUser message: {question}"
        answer = self._call_ollama_text(system=system, user=user, max_output_tokens=160, temperature=0.3)
        if answer:
            cleaned = self._cleanup_answer(answer)
            if cleaned:
                return cleaned
        return "你好，我可以協助查詢財務資料、報銷規範，或整合兩者的問題。"

    def generate_sql(self, question: str, db_schema: str, skill_instructions: str) -> Optional[str]:
        system = (
            "You generate one read-only SQLite query for finance analytics. "
            "Follow the provided skill instructions. "
            "Return SQL only, no markdown, no explanation. "
            "Use only the provided schema. "
            "Field formats: record_id is INTEGER primary key; month is DATE in YYYY-MM-DD format; revenue is INTEGER amount; expense is INTEGER amount; net_profit is INTEGER amount. "
            "When filtering by month, always compare against a full YYYY-MM-DD date value, not a partial YYYY-MM string. "
            "Correct example: SELECT revenue FROM monthly_finance WHERE month = '2025-06-01'. "
            "Also valid: SELECT revenue FROM monthly_finance WHERE month LIKE '2025-06-%'. "
            "Incorrect example: SELECT revenue FROM monthly_finance WHERE month = '2025-06'. "
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

    def decompose_hybrid_question(self, question: str) -> Optional[HybridQuestionParts]:
        system = (
            "You split a finance hybrid question into two sub-questions. "
            "Return strict JSON only with keys sql_question and policy_question. "
            "sql_question must contain only the structured-data part answerable from SQLite. "
            "policy_question must contain only the document-grounded policy or approval part answerable from finance rules. "
            "Do not answer the question. "
            "Preserve months, dates, amounts, thresholds, and approval conditions exactly."
        )
        user = (
            f"Question: {question}\n"
            'Output JSON format: {"sql_question":"...","policy_question":"..."}\n'
            "Example input: 2025 年 6 月淨利是多少？如果當月有一筆 60,000 元的採購，依規範需要哪些人核准？\n"
            'Example output: {"sql_question":"2025 年 6 月淨利是多少？","policy_question":"如果當月有一筆 60,000 元的採購，依規範需要哪些人核准？"}'
        )
        raw = self._call_ollama_text(system=system, user=user, max_output_tokens=180, temperature=0.0)
        return self._parse_hybrid_question_parts(raw)

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
            "Write a concise, clear, professional answer in Traditional Chinese used in Taiwan only. "
            "Never use Simplified Chinese characters. "
            "Follow the provided skill instructions. "
            "Stay grounded to the provided evidence. "
            "Do not invent facts. "
            "Do not output field labels such as sql, rows, summary, evidence, answer, route, citations, or markdown fences. "
            "Return only the final user-facing answer."
        )
        evidence_block = "\n- ".join(evidence_lines) if evidence_lines else "無"
        user = (
            f"Skill instructions:\n{skill_instructions}\n\n"
            f"Question: {question}\n"
            f"Route: {route}\n"
            f"Draft answer: {draft_answer}\n"
            f"Evidence:\n- {evidence_block}"
        )
        refined = self._call_ollama_text(system=system, user=user, max_output_tokens=220, temperature=0.2)
        if refined:
            cleaned = self._cleanup_answer(refined)
            if self._is_user_facing_answer(route, cleaned):
                return cleaned
        return self._fallback_answer(route, draft_answer)

    def write_rag_answer(self, question: str, context_chunks: list[str], skill_instructions: str) -> str:
        system = (
            "You are a finance policy QA assistant. "
            "Answer in concise, professional Traditional Chinese used in Taiwan only. "
            "Never use Simplified Chinese characters. "
            "Follow the provided skill instructions. "
            "Use only the provided retrieved document context. "
            "If any retrieved chunk directly states the answer, answer from it and do not say insufficient evidence. "
            "Treat a clearly stated policy amount, allowance, deadline, approver list, approval threshold, reimbursement rule, or procurement rule in the retrieved text as sufficient evidence. "
            "For approval, reimbursement, deadline, allowance, threshold, and procurement questions, extract the exact rule from the retrieved text. "
            "Only say insufficient evidence when none of the retrieved chunks contains a directly applicable rule. "
            "If the user question mixes a policy question with a separate SQL or numeric question, answer only the policy part from the document context. "
            "Do not say the document lacks the SQL answer if the policy answer is available. "
            "Do not describe what the document does not cover unless that missing coverage prevents answering the policy sub-question itself. "
            "Answer the question directly in 1 to 2 sentences. "
            "Do not repeat the same fact in multiple formats. "
            "Do not add bullet points unless the user explicitly asks for a list. "
            "Do not include meta-evidence phrases such as '源文出自', '明確指出', '根據文件內容', or similar commentary about the evidence. "
            "Only include extra detail when it is necessary to make the answer unambiguous. "
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
            cleaned = self._cleanup_answer(answer)
            if cleaned:
                return cleaned
        if context_chunks:
            snippet = context_chunks[0].strip().replace("\n", " ")
            return f"依據檢索到的文件內容，相關依據為：{snippet[:160]}。"
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
        confidence_raw = data.get("confidence", 0.0)
        try:
            confidence = float(confidence_raw)
        except (TypeError, ValueError):
            confidence = 0.0
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
    def _parse_hybrid_question_parts(raw: str | None) -> Optional[HybridQuestionParts]:
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

        sql_question = data.get("sql_question")
        policy_question = data.get("policy_question")
        if not isinstance(sql_question, str) or not sql_question.strip():
            return None
        if not isinstance(policy_question, str) or not policy_question.strip():
            return None
        return HybridQuestionParts(
            sql_question=sql_question.strip(),
            policy_question=policy_question.strip(),
        )

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
            r"(?im)^route:\s*",
        ]
        for pattern in label_patterns:
            cleaned = re.sub(pattern, "", cleaned)

        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
        return cleaned

    @staticmethod
    def _is_user_facing_answer(route: str, text: str) -> bool:
        if not text:
            return False

        lower = text.lower()
        if "```" in text:
            return False
        if route in {"sql", "hybrid"} and "select " in lower:
            return False
        if lower.startswith("{") and lower.endswith("}"):
            return False
        return True

    @staticmethod
    def _fallback_answer(route: str, draft_answer: str) -> str:
        cleaned = draft_answer.strip()
        if route == "sql":
            return f"根據資料庫查詢結果，{cleaned}"
        if route == "rag":
            return cleaned or "insufficient evidence"
        if route == "chat":
            return cleaned or "你好，我可以協助查詢財務相關問題。"
        return f"綜合資料庫與文件證據，{cleaned}"

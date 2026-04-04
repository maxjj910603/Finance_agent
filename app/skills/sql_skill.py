from __future__ import annotations

import re

from app.schemas import EvidenceItem
from app.services.db import DBService
from app.services.llm_client import LLMClient


class SQLSkill:
    def __init__(self, db_service: DBService, llm_client: LLMClient) -> None:
        self.db_service = db_service
        self.llm_client = llm_client

    def run(self, question: str, skill_instructions: str) -> tuple[str, list[EvidenceItem]]:
        llm_sql = self.llm_client.generate_sql(question, self.db_service.schema_text(), skill_instructions)

        sql_source = "llm"
        if self._is_safe_select(llm_sql):
            sql = self._normalize_sql(llm_sql)
        else:
            sql = self._heuristic_sql(question)
            sql_source = "fallback"

        try:
            rows = self.db_service.run_select(sql)
        except Exception:
            sql = self._heuristic_sql(question)
            rows = self.db_service.run_select(sql)
            sql_source = "fallback_on_execute_error"

        summary = self._summarize(rows)
        evidence = [
            EvidenceItem(type="sql", source="sqlite:monthly_finance", detail=f"sql_source={sql_source}"),
            EvidenceItem(type="sql", source="sqlite:monthly_finance", detail=f"query={sql}"),
            EvidenceItem(type="sql", source="sqlite:monthly_finance", detail=f"rows={len(rows)}; {summary}"),
        ]
        answer = self.llm_client.write_answer(
            question=question,
            route="sql",
            draft_answer=summary,
            evidence_lines=[f"{item.source}: {item.detail}" for item in evidence],
            skill_instructions=skill_instructions,
        )
        return answer, evidence

    def _heuristic_sql(self, question: str) -> str:
        q = question.lower()

        if "highest" in q or "max" in q or "最高" in question:
            return "SELECT month, net_profit FROM monthly_finance ORDER BY net_profit DESC LIMIT 1"
        if "lowest" in q or "min" in q or "最低" in question:
            return "SELECT month, net_profit FROM monthly_finance ORDER BY net_profit ASC LIMIT 1"
        if "average" in q or "平均" in question:
            return "SELECT AVG(net_profit) AS avg_net_profit FROM monthly_finance"
        if "revenue" in q or "營收" in question:
            return "SELECT month, revenue FROM monthly_finance ORDER BY month ASC LIMIT 12"
        if "expense" in q or "支出" in question or "費用" in question:
            return "SELECT month, expense FROM monthly_finance ORDER BY month ASC LIMIT 12"
        return "SELECT month, revenue, expense, net_profit FROM monthly_finance ORDER BY month ASC LIMIT 12"

    @staticmethod
    def _is_safe_select(sql: str | None) -> bool:
        if not sql:
            return False

        raw = sql.strip()
        if not raw:
            return False
        s = raw.lower()

        if ";" in s[:-1]:
            return False
        if s.endswith(";"):
            s = s[:-1].strip()

        if not s.startswith("select"):
            return False

        forbidden = [
            " insert ",
            " update ",
            " delete ",
            " drop ",
            " alter ",
            " create ",
            " truncate ",
            " attach ",
            " detach ",
            " pragma ",
            " vacuum ",
            " reindex ",
        ]
        padded = f" {s} "
        if any(token in padded for token in forbidden):
            return False

        if "from monthly_finance" not in s and "avg(" not in s and "max(" not in s and "min(" not in s:
            return False

        if re.search(r"select\s+.*'[^']+'\s+as\s+\w+", s, re.IGNORECASE | re.DOTALL):
            return False
        if re.search(r'select\s+.*"[^"]+"\s+as\s+\w+', s, re.IGNORECASE | re.DOTALL):
            return False

        return True

    @staticmethod
    def _normalize_sql(sql: str) -> str:
        s = sql.strip()
        if s.endswith(";"):
            s = s[:-1].strip()

        lower = s.lower()
        is_aggregate = any(fn in lower for fn in ["count(", "sum(", "avg(", "min(", "max("])
        if (not is_aggregate) and (" limit " not in lower):
            s = f"{s} LIMIT 50"
        return s

    @staticmethod
    def _summarize(rows: list) -> str:
        if not rows:
            return "查無符合條件的資料。"

        first = rows[0]
        keys = list(first.keys())
        label_map = {
            "month": "月份",
            "revenue": "營收",
            "expense": "支出",
            "net_profit": "淨利",
            "highest_net_profit": "最高淨利",
            "lowest_net_profit": "最低淨利",
            "avg_net_profit": "平均淨利",
        }

        def format_key(key: str) -> str:
            return label_map.get(key, key)

        if len(rows) == 1 and len(keys) == 1:
            key = keys[0]
            return f"{format_key(key)}為 {first[key]}。"
        if len(rows) == 1 and len(keys) == 2:
            if "month" in first:
                metric_keys = [key for key in keys if key != "month"]
                if len(metric_keys) == 1:
                    metric_key = metric_keys[0]
                    return f"{first['month']} 的{format_key(metric_key)}為 {first[metric_key]}。"
            return "，".join([f"{format_key(key)}為 {first[key]}" for key in keys]) + "。"

        preview = []
        for row in rows[:3]:
            preview.append("，".join([f"{format_key(key)}={row[key]}" for key in row.keys()]))
        return "前幾筆結果為：" + "；".join(preview) + "。"

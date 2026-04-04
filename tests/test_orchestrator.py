import unittest
from dataclasses import dataclass
from pathlib import Path

from app.orchestrator import Orchestrator
from app.schemas import EvidenceItem, RouterResult


@dataclass
class StubSkillSpec:
    name: str
    description: str
    instructions: str
    path: Path


class StubRegistry:
    def __init__(self) -> None:
        self.skills = {
            "chat-skill": StubSkillSpec("chat-skill", "chat route", "chat instructions", Path("chat")),
            "sql-skill": StubSkillSpec("sql-skill", "sql route", "sql instructions", Path("sql")),
            "rag-skill": StubSkillSpec("rag-skill", "rag route", "rag instructions", Path("rag")),
            "hybrid-skill": StubSkillSpec("hybrid-skill", "hybrid route", "hybrid instructions", Path("hybrid")),
        }

    def all(self) -> list[StubSkillSpec]:
        return list(self.skills.values())

    def get(self, name: str) -> StubSkillSpec:
        return self.skills[name]


class StubLLMClient:
    def __init__(self, route_result: RouterResult | None) -> None:
        self.route_result = route_result

    def classify_route(self, question: str, route_summaries: list[dict[str, str]]) -> RouterResult | None:
        return self.route_result


class StubChatSkill:
    def run(self, question: str) -> str:
        return "chat answer"


class StubSQLSkill:
    def run(self, question: str, skill_instructions: str) -> tuple[str, list[EvidenceItem]]:
        return "sql answer", [EvidenceItem(type="sql", source="sqlite", detail="query=SELECT 1")]


class StubRAGSkill:
    def run(self, question: str, skill_instructions: str) -> tuple[str, list[EvidenceItem]]:
        return "rag answer", [EvidenceItem(type="rag", source="doc.txt", detail="snippet=test")]


class StubHybridSkill:
    def run(
        self,
        question: str,
        sql_answer: str,
        rag_answer: str,
        sql_evidence: list[EvidenceItem],
        rag_evidence: list[EvidenceItem],
        skill_instructions: str,
    ) -> tuple[str, list[EvidenceItem]]:
        return "hybrid answer", sql_evidence + rag_evidence


class OrchestratorRoutingTests(unittest.TestCase):
    def build_orchestrator(self, route_result: RouterResult | None) -> Orchestrator:
        orchestrator = Orchestrator.__new__(Orchestrator)
        orchestrator.llm_client = StubLLMClient(route_result)
        orchestrator.skill_registry = StubRegistry()
        orchestrator.chat_skill = StubChatSkill()
        orchestrator.sql_skill = StubSQLSkill()
        orchestrator.rag_skill = StubRAGSkill()
        orchestrator.hybrid_skill = StubHybridSkill()
        return orchestrator

    def test_invalid_or_missing_route_defaults_to_hybrid(self) -> None:
        orchestrator = self.build_orchestrator(None)
        result = orchestrator.ask("unknown")
        self.assertEqual(result.route, "hybrid")

    def test_valid_route_is_respected(self) -> None:
        orchestrator = self.build_orchestrator(RouterResult(route="rag", reason="policy question", confidence=0.9))
        result = orchestrator.ask("policy question")
        self.assertEqual(result.route, "rag")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from pathlib import Path

from app.schemas import AssistantResponse
from app.services.db import DBService


class Orchestrator:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(__file__).resolve().parents[1]
        self.db_service = DBService(self.base_dir / "data" / "db" / "finance_agent.db")
        self.db_service.ensure_seeded()

    def ask(self, question: str) -> AssistantResponse:
        _ = question
        return AssistantResponse(
            answer="Not implemented yet.",
            route="chat",
            evidence=[],
        )

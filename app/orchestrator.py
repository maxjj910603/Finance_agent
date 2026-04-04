from __future__ import annotations

from pathlib import Path

from app.schemas import AssistantResponse


class Orchestrator:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(__file__).resolve().parents[1]

    def ask(self, question: str) -> AssistantResponse:
        _ = question
        return AssistantResponse(
            answer="Not implemented yet.",
            route="chat",
            evidence=[],
        )

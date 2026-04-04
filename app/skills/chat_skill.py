from __future__ import annotations

from app.services.llm_client import LLMClient


class ChatSkill:
    def __init__(self, llm_client: LLMClient, instructions: str) -> None:
        self.llm_client = llm_client
        self.instructions = instructions

    def run(self, question: str) -> str:
        return self.llm_client.chat_answer(question, self.instructions)

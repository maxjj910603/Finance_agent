from __future__ import annotations

from pathlib import Path

from app.schemas import AssistantResponse
from app.services.db import DBService
from app.services.embeddings import EmbeddingService
from app.services.ingestion import IngestionService
from app.services.llm_client import LLMClient
from app.services.retriever import Retriever
from app.services.skill_registry import SkillRegistry
from app.services.vector_store import VectorStore
from app.skills.chat_skill import ChatSkill
from app.skills.hybrid_skill import HybridSkill
from app.skills.rag_skill import RAGSkill
from app.skills.sql_skill import SQLSkill


class Orchestrator:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(__file__).resolve().parents[1]
        self.db_service = DBService(self.base_dir / "data" / "db" / "finance_agent.db")
        self.db_service.ensure_seeded()

        self.llm_client = LLMClient()
        self.skill_registry = SkillRegistry(self.base_dir / ".agents" / "skills")

        self.sql_skill = SQLSkill(self.db_service, self.llm_client)
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore(self.base_dir / "data" / "vector_store", collection_name="finance_policy")
        self.retriever = Retriever(self.embedding_service, self.vector_store)
        self.rag_skill = RAGSkill(self.retriever, self.llm_client)
        self.hybrid_skill = HybridSkill(self.llm_client)
        self.chat_skill = ChatSkill(self.llm_client, self.skill_registry.get("chat-skill").instructions)
        self._ensure_vector_index()

    def ask(self, question: str) -> AssistantResponse:
        route_result = self.llm_client.classify_skill(question, self.skill_registry.summaries())
        skill_name = route_result.route if route_result is not None else "hybrid-skill"
        if skill_name not in {skill.name for skill in self.skill_registry.all()}:
            skill_name = "hybrid-skill"

        route = skill_name.replace("-skill", "")

        if skill_name == "chat-skill":
            answer = self.chat_skill.run(question)
            return AssistantResponse(answer=answer, route="chat", evidence=[])

        if skill_name == "sql-skill":
            skill = self.skill_registry.get("sql-skill")
            answer, evidence = self.sql_skill.run(question, skill.instructions)
            polished = self._write_answer(question, "sql", answer, evidence, skill.instructions)
            return AssistantResponse(answer=polished, route="sql", evidence=evidence)

        if skill_name == "rag-skill":
            skill = self.skill_registry.get("rag-skill")
            answer, evidence = self.rag_skill.run(question, skill.instructions)
            return AssistantResponse(answer=answer, route="rag", evidence=evidence)

        sql_spec = self.skill_registry.get("sql-skill")
        rag_spec = self.skill_registry.get("rag-skill")
        hybrid_spec = self.skill_registry.get("hybrid-skill")
        sql_answer, sql_evidence = self.sql_skill.run(question, sql_spec.instructions)
        rag_answer, rag_evidence = self.rag_skill.run(question, rag_spec.instructions)
        answer, evidence = self.hybrid_skill.run(
            question,
            sql_answer,
            rag_answer,
            sql_evidence,
            rag_evidence,
            hybrid_spec.instructions,
        )
        return AssistantResponse(answer=answer, route=route, evidence=evidence)

    def _write_answer(
        self,
        question: str,
        route: str,
        answer: str,
        evidence: list,
        skill_instructions: str,
    ) -> str:
        evidence_lines = [f"{item.source}: {item.detail}" for item in evidence[:4]]
        return self.llm_client.write_answer(question, route, answer, evidence_lines, skill_instructions)

    def _ensure_vector_index(self) -> None:
        if self.vector_store.count() > 0:
            return

        txt_files = sorted(self.base_dir.glob("*.txt"))
        if not txt_files:
            return

        ingestion = IngestionService(self.embedding_service, self.vector_store)
        for doc_path in txt_files:
            if doc_path.name.lower() == "requirements.txt":
                continue
            ingestion.ingest_file(doc_path)

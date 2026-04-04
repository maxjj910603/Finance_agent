import tempfile
import unittest
from pathlib import Path

from app.services.ingestion import IngestionService
from app.services.retriever import Retriever
from app.services.vector_store import VectorStore


class FakeEmbeddingService:
    def embed_text(self, text: str) -> list[float]:
        lower_text = text.lower()
        return [
            1.0 if "budget" in lower_text or "預算" in text else 0.0,
            1.0 if "reimburse" in lower_text or "報銷" in text else 0.0,
            1.0 if "approve" in lower_text or "核准" in text else 0.0,
        ]


class RAGPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.base = Path(self.tmp_dir.name)
        self.doc_path = self.base / "finance_policy.txt"
        self.doc_path.write_text(
            "預算追加申請須提供主管核准。\n"
            "報銷申請必須附上合法憑證。\n",
            encoding="utf-8",
        )
        self.vector_store = VectorStore(self.base / "chroma_test", collection_name="test_collection")
        self.embedding_service = FakeEmbeddingService()

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_ingestion_and_retrieval_pipeline(self) -> None:
        ingestion = IngestionService(
            embedding_service=self.embedding_service,
            vector_store=self.vector_store,
            chunk_size=20,
            chunk_overlap=0,
        )
        chunk_count = ingestion.ingest_file(self.doc_path)
        self.assertGreaterEqual(chunk_count, 1)
        self.assertEqual(self.vector_store.count(), chunk_count)

        retriever = Retriever(self.embedding_service, self.vector_store)
        results = retriever.retrieve("預算追加需要核准嗎？", top_k=2)
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("finance_policy.txt", results[0]["metadata"]["source"])

    def test_default_chunk_settings_match_runtime_configuration(self) -> None:
        ingestion = IngestionService(
            embedding_service=self.embedding_service,
            vector_store=self.vector_store,
        )
        self.assertEqual(ingestion.chunk_size, 150)
        self.assertEqual(ingestion.chunk_overlap, 30)


if __name__ == "__main__":
    unittest.main()

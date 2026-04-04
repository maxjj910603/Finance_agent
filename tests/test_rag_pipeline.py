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
            1.0 if "預算" in text or "budget" in lower_text else 0.0,
            1.0 if "報銷" in text or "reimburse" in lower_text else 0.0,
            1.0 if "核准" in text or "approve" in lower_text else 0.0,
        ]


class RAGPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.base = Path(self.tmp_dir.name)
        self.doc_path = self.base / "finance_policy.txt"
        self.doc_path.write_text(
            "預算申請需要部門主管核准。\n"
            "報銷單據必須附上原始憑證。\n",
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
        results = retriever.retrieve("預算核准規則是什麼？", top_k=2)
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("finance_policy.txt", results[0]["metadata"]["source"])


if __name__ == "__main__":
    unittest.main()

import unittest

from app.orchestrator import Orchestrator


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = Orchestrator()

    def test_chat_route_returns_string_answer(self) -> None:
        result = self.app.ask("你好").to_dict()
        self.assertIn(result["route"], {"chat", "sql", "rag", "hybrid"})
        self.assertIsInstance(result["answer"], str)

    def test_sql_question_returns_contract(self) -> None:
        result = self.app.ask("What is the highest net profit month?").to_dict()
        self.assertIn(result["route"], {"chat", "sql", "rag", "hybrid"})
        self.assertIn("answer", result)
        self.assertIn("evidence", result)

    def test_rag_question_returns_contract(self) -> None:
        result = self.app.ask("報銷需要哪些憑證？").to_dict()
        self.assertIn(result["route"], {"chat", "sql", "rag", "hybrid"})
        self.assertIn("answer", result)
        self.assertIn("evidence", result)

    def test_hybrid_question_returns_contract(self) -> None:
        result = self.app.ask("最高淨利月份是何時，是否需要額外預算審批？").to_dict()
        self.assertIn(result["route"], {"chat", "sql", "rag", "hybrid"})
        self.assertIn("answer", result)
        self.assertIn("evidence", result)


if __name__ == "__main__":
    unittest.main()

import unittest

from app.orchestrator import Orchestrator


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = Orchestrator()

    def test_chat_route_returns_contract(self) -> None:
        result = self.app.ask("hello").to_dict()
        self.assertIn(result["route"], {"chat", "sql", "rag", "hybrid"})
        self.assertIsInstance(result["answer"], str)
        self.assertIn("evidence", result)

    def test_sql_question_returns_contract(self) -> None:
        result = self.app.ask("What is the highest net profit month?").to_dict()
        self.assertIn(result["route"], {"chat", "sql", "rag", "hybrid"})
        self.assertIn("answer", result)
        self.assertIn("evidence", result)

    def test_rag_question_returns_contract(self) -> None:
        result = self.app.ask("根據報銷規範，哪些費用不得報銷？").to_dict()
        self.assertIn(result["route"], {"chat", "sql", "rag", "hybrid"})
        self.assertIn("answer", result)
        self.assertIn("evidence", result)

    def test_hybrid_question_returns_contract(self) -> None:
        result = self.app.ask("哪一個月份淨利最高，且該月份若要追加 20% 預算需要什麼程序？").to_dict()
        self.assertIn(result["route"], {"chat", "sql", "rag", "hybrid"})
        self.assertIn("answer", result)
        self.assertIn("evidence", result)


if __name__ == "__main__":
    unittest.main()

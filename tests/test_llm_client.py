import unittest

from app.services.llm_client import LLMClient


class LLMClientTests(unittest.TestCase):
    def test_parse_route_accepts_contract_route(self) -> None:
        result = LLMClient._parse_route('{"route":"sql","reason":"structured metric","confidence":0.92}')
        self.assertIsNotNone(result)
        self.assertEqual(result.route, "sql")

    def test_parse_route_rejects_skill_name(self) -> None:
        result = LLMClient._parse_route('{"route":"sql-skill","reason":"old format","confidence":0.8}')
        self.assertIsNone(result)

    def test_fallback_answer_for_sql_is_user_facing(self) -> None:
        answer = LLMClient._fallback_answer("sql", "month 為 2025-06-01，net_profit 為 420000。")
        self.assertIn("根據資料庫查詢結果", answer)

    def test_parse_route_rejects_chat_like_invalid_text(self) -> None:
        result = LLMClient._parse_route('{"route":"payment-policy","reason":"approval threshold question","confidence":0.88}')
        self.assertIsNone(result)

    def test_cleanup_answer_normalizes_common_simplified_chinese(self) -> None:
        client = LLMClient()
        answer = client._cleanup_answer("根据报销规范，金额超过 10000 的采购需要审批。")
        self.assertEqual(answer, "根據報銷規範，金額超過 10000 的採購需要審批。")


if __name__ == "__main__":
    unittest.main()

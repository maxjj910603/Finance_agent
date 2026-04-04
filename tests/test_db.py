import tempfile
import unittest
from pathlib import Path

from app.services.db import DBService


class DBServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "finance_demo.db"
        self.db = DBService(self.db_path)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_ensure_seeded_creates_table_and_rows(self) -> None:
        self.db.ensure_seeded()
        rows = self.db.run_select("SELECT COUNT(1) AS cnt FROM monthly_finance")
        self.assertEqual(rows[0]["cnt"], 6)

    def test_schema_text_mentions_monthly_finance(self) -> None:
        schema = self.db.schema_text()
        self.assertIn("monthly_finance", schema)
        self.assertIn("net_profit", schema)


if __name__ == "__main__":
    unittest.main()

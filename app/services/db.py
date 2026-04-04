from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List


class DBService:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def ensure_seeded(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS monthly_finance (
                    record_id INTEGER PRIMARY KEY,
                    month DATE NOT NULL,
                    revenue INTEGER NOT NULL,
                    expense INTEGER NOT NULL,
                    net_profit INTEGER NOT NULL
                )
                """
            )
            cur.execute("SELECT COUNT(1) FROM monthly_finance")
            row_count = cur.fetchone()[0]
            if row_count == 0:
                cur.executemany(
                    """
                    INSERT INTO monthly_finance (record_id, month, revenue, expense, net_profit)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [
                        (1, "2025-01-01", 1200000, 950000, 250000),
                        (2, "2025-02-01", 1350000, 980000, 370000),
                        (3, "2025-03-01", 1280000, 1020000, 260000),
                        (4, "2025-04-01", 1420000, 1100000, 320000),
                        (5, "2025-05-01", 1500000, 1150000, 350000),
                        (6, "2025-06-01", 1600000, 1180000, 420000),
                    ],
                )
            conn.commit()
        finally:
            conn.close()

    def run_select(self, sql: str) -> List[sqlite3.Row]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()
            cur.execute(sql)
            return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def schema_text() -> str:
        return (
            "monthly_finance(record_id INTEGER PK, month DATE, revenue INTEGER, "
            "expense INTEGER, net_profit INTEGER)"
        )

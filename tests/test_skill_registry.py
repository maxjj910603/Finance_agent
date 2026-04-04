import unittest
from pathlib import Path

from app.services.skill_registry import SkillRegistry


class SkillRegistryTests(unittest.TestCase):
    def test_registry_loads_skill_metadata_and_body(self) -> None:
        registry = SkillRegistry(Path(".agents/skills"))
        summaries = registry.summaries()
        names = {item["name"] for item in summaries}

        self.assertIn("chat-skill", names)
        self.assertIn("sql-skill", names)
        self.assertIn("rag-skill", names)
        self.assertIn("hybrid-skill", names)

        sql_skill = registry.get("sql-skill")
        self.assertIn("Workflow", sql_skill.instructions)
        self.assertIn("monthly_finance", sql_skill.instructions)


if __name__ == "__main__":
    unittest.main()

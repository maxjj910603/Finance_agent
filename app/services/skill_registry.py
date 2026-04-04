from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SkillSpec:
    name: str
    description: str
    instructions: str
    path: Path


class SkillRegistry:
    def __init__(self, skills_dir: Path) -> None:
        self.skills_dir = skills_dir
        self._skills = self._load_skills()

    def all(self) -> list[SkillSpec]:
        return list(self._skills.values())

    def get(self, name: str) -> SkillSpec:
        return self._skills[name]

    def summaries(self) -> list[dict[str, str]]:
        return [{"name": skill.name, "description": skill.description} for skill in self.all()]

    def _load_skills(self) -> dict[str, SkillSpec]:
        skills: dict[str, SkillSpec] = {}
        if not self.skills_dir.exists():
            return skills

        for skill_dir in sorted(self.skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            name, description, instructions = self._parse_skill_file(skill_md)
            skills[name] = SkillSpec(name=name, description=description, instructions=instructions, path=skill_md)
        return skills

    @staticmethod
    def _parse_skill_file(path: Path) -> tuple[str, str, str]:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            raise ValueError(f"Missing frontmatter in {path}")

        parts = text.split("---", 2)
        if len(parts) < 3:
            raise ValueError(f"Invalid frontmatter in {path}")

        metadata_lines = parts[1].strip().splitlines()
        body = parts[2].lstrip()

        metadata: dict[str, str] = {}
        for line in metadata_lines:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

        name = metadata.get("name")
        description = metadata.get("description")
        if not name or not description:
            raise ValueError(f"Missing name/description in {path}")
        return name, description, body

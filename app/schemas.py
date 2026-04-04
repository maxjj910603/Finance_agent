from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Literal

RouteName = Literal["chat", "sql", "rag", "hybrid"]


@dataclass
class RouterResult:
    route: RouteName
    reason: str
    confidence: float


@dataclass
class EvidenceItem:
    type: str
    source: str
    detail: str


@dataclass
class AssistantResponse:
    answer: str
    route: RouteName
    evidence: List[EvidenceItem]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "route": self.route,
            "evidence": [asdict(item) for item in self.evidence],
        }

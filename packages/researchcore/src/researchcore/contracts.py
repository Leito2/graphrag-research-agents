"""Research contracts (PLAN §5.1). Every claim in a report must point to Evidence with provenance."""
from typing import Literal

from pydantic import BaseModel, Field

Source = Literal["graph", "docs", "web", "vision", "code"]
ContradictionKind = Literal["graph_vs_web", "doc_vs_graph", "visual_vs_graph", "numeric"]
Status = Literal["planning", "researching", "auditing", "synthesizing", "awaiting_human", "done", "error"]


class SubQuestion(BaseModel):
    id: str
    text: str
    sources: list[Source] = Field(min_length=1)


class Evidence(BaseModel):
    id: str
    sub_question_id: str
    source: Source
    content_hash: str                      # SHA-256 of the evidence text (logged instead of content)
    locator: str                           # node id / chunk id / URL / image id / sandbox run id
    summary: str
    untrusted: bool = False                # web or uploaded content: data, never instructions (ADR-5)


class Contradiction(BaseModel):
    kind: ContradictionKind
    evidence_ids: tuple[str, str]
    severity: Literal["low", "high"]
    resolved: bool = False


class Citation(BaseModel):
    claim: str
    evidence_ids: list[str] = Field(min_length=1)


class Report(BaseModel):
    answer: str | None                     # None => "insufficient evidence"
    citations: list[Citation] = []
    confidence: Literal["high", "medium", "degraded"]
    unresolved: list[Contradiction] = []
    high_impact: bool = False              # recommends blocking/reporting => human approval (ADR-9)


class ResearchState(BaseModel):
    question: str
    thread_id: str
    plan: list[SubQuestion] = []
    evidence: list[Evidence] = []
    contradictions: list[Contradiction] = []
    iteration: int = 0
    max_iterations: int = 3
    report: Report | None = None
    status: Status = "planning"

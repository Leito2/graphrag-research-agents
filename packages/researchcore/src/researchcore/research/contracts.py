"""Research contracts (PLAN §5). Every claim in a research note must point to Evidence with provenance."""
from typing import Literal

from pydantic import BaseModel, Field

Mode = Literal["ask", "deep-research", "staleness-audit", "gap-map", "study-plan"]
Source = Literal["vault", "web", "scholar", "vision", "code"]
FindingKind = Literal["note_vs_web", "note_vs_note", "visual_vs_text", "numeric", "outdated"]
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
    locator: str                           # "note.md#Heading" / URL / DOI / "pypi:pkg==x" / sandbox run id
    summary: str
    untrusted: bool = False                # web content: data, never instructions (ADR-6)


class AuditFinding(BaseModel):
    kind: FindingKind
    evidence_ids: tuple[str, str]
    severity: Literal["low", "high"]
    resolved: bool = False


class Citation(BaseModel):
    claim: str
    evidence_ids: list[str] = Field(min_length=1)


class ResearchNote(BaseModel):
    """What the Writer saves into the vault's output folder (after human approval, ADR-11)."""
    title: str
    mode: Mode
    body: str | None                       # None => "insufficient evidence"
    citations: list[Citation] = []
    confidence: Literal["high", "medium", "degraded"]
    findings: list[AuditFinding] = []
    suggested_edits: list[str] = []        # proposals for existing notes, never applied (ADR-3)


class ResearchState(BaseModel):
    question: str
    mode: Mode = "ask"
    thread_id: str
    plan: list[SubQuestion] = []
    evidence: list[Evidence] = []
    findings: list[AuditFinding] = []
    iteration: int = 0
    max_iterations: int = 3
    note: ResearchNote | None = None
    approved: bool | None = None           # human decision at the interrupt
    status: Status = "planning"

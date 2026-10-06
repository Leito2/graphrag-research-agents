"""Deterministic Leader (inherited ADR-HARNESS-001, PLAN ADR-2): transitions read the state, never an LLM."""
from typing import Literal

from researchcore.contracts import ResearchState

Next = Literal["planner", "fact_auditor", "synthesis", "human", "end"]


def next_step(state: ResearchState) -> Next:
    if state.status == "planning":
        return "planner"
    if state.status == "researching":
        return "fact_auditor"
    if state.status == "auditing":
        open_high = [c for c in state.contradictions if c.severity == "high" and not c.resolved]
        if open_high and state.iteration < state.max_iterations:
            return "planner"               # re-investigate the contradictions (bounded loop)
        return "synthesis"                 # converged, or bound reached => degraded confidence
    if state.status == "synthesizing" and state.report is not None:
        return "human" if state.report.high_impact else "end"
    return "end"

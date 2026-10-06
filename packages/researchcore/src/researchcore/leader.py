"""Deterministic Leader (inherited ADR-HARNESS-001, PLAN ADR-2): transitions read the state, never an LLM."""
from typing import Literal

from researchcore.contracts import ResearchState

Next = Literal["planner", "fact_auditor", "synthesis", "human", "writer", "end"]


def next_step(state: ResearchState) -> Next:
    if state.status == "planning":
        return "planner"
    if state.status == "researching":
        return "fact_auditor"
    if state.status == "auditing":
        open_high = [f for f in state.findings if f.severity == "high" and not f.resolved]
        if open_high and state.iteration < state.max_iterations:
            return "planner"               # re-investigate (bounded loop)
        return "synthesis"                 # converged, or bound reached => degraded confidence
    if state.status == "synthesizing" and state.note is not None:
        return "human"                     # nothing is written to the vault without approval (ADR-11)
    if state.status == "awaiting_human" and state.approved is not None:
        return "writer" if state.approved else "end"
    return "end"

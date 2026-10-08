from researchcore.research.contracts import AuditFinding, ResearchNote, ResearchState
from researchcore.research.leader import next_step


def state(**kw) -> ResearchState:
    return ResearchState(question="q", thread_id="t", **kw)


HIGH = AuditFinding(kind="outdated", evidence_ids=("e1", "e2"), severity="high")
NOTE = ResearchNote(title="GraphRAG", mode="deep-research", body="...", confidence="high")


def test_high_finding_loops_back_to_planner():
    assert next_step(state(status="auditing", findings=[HIGH], iteration=1)) == "planner"


def test_loop_is_bounded_and_falls_through_to_synthesis():
    assert next_step(state(status="auditing", findings=[HIGH], iteration=3)) == "synthesis"


def test_low_or_resolved_findings_do_not_loop():
    low = HIGH.model_copy(update={"severity": "low"})
    done = HIGH.model_copy(update={"resolved": True})
    assert next_step(state(status="auditing", findings=[low, done])) == "synthesis"


def test_nothing_is_written_without_human_approval():
    assert next_step(state(status="synthesizing", note=NOTE)) == "human"
    assert next_step(state(status="awaiting_human", note=NOTE)) == "end"          # still waiting
    assert next_step(state(status="awaiting_human", note=NOTE, approved=True)) == "writer"
    assert next_step(state(status="awaiting_human", note=NOTE, approved=False)) == "end"

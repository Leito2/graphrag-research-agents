from researchcore.contracts import Contradiction, Report, ResearchState
from researchcore.leader import next_step


def state(**kw) -> ResearchState:
    return ResearchState(question="q", thread_id="t", **kw)


HIGH = Contradiction(kind="graph_vs_web", evidence_ids=("e1", "e2"), severity="high")


def test_high_contradiction_loops_back_to_planner():
    assert next_step(state(status="auditing", contradictions=[HIGH], iteration=1)) == "planner"


def test_loop_is_bounded_and_falls_through_to_synthesis():
    assert next_step(state(status="auditing", contradictions=[HIGH], iteration=3)) == "synthesis"


def test_low_or_resolved_contradictions_do_not_loop():
    low = HIGH.model_copy(update={"severity": "low"})
    done = HIGH.model_copy(update={"resolved": True})
    assert next_step(state(status="auditing", contradictions=[low, done])) == "synthesis"


def test_high_impact_report_needs_human():
    report = Report(answer="block account", confidence="high", high_impact=True)
    assert next_step(state(status="synthesizing", report=report)) == "human"
    low_impact = report.model_copy(update={"high_impact": False})
    assert next_step(state(status="synthesizing", report=low_impact)) == "end"

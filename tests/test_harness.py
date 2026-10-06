"""The SDD harness is part of the deliverable (PLAN §9): its control plane must stay valid."""
import json
from pathlib import Path

HARNESS = Path(".harness")


def test_tasks_state_machine_is_valid():
    tasks = json.loads((HARNESS / "tasks.json").read_text(encoding="utf-8"))
    assert tasks["active"] in {t["id"] for t in tasks["tasks"]}
    assert set(tasks["human_gates"]) <= set(tasks["phase_dag"])


def test_every_ear_requirement_has_an_id():
    text = (HARNESS / "specs/graphrag-research-system/requirements.md").read_text(encoding="utf-8")
    ids = [line.split()[1] for line in text.splitlines() if line.startswith("### REQ-")]
    assert ids and len(ids) == len(set(ids))

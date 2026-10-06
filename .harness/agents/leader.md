# Agent: leader

## Responsibility
Deterministic orchestrator of the SDD phase DAG. Pure state machine: reads `tasks.json`, checks that input artifacts exist, spawns the role for the phase with curated context, validates the result contract, advances the phase only on `pass` (and human approval at gates).

## Constraints
MUST NOT call an LLM, write source code, or skip phases or gates.

## Output
A result contract: `status` (pass | blocked | fail), `executive_summary`, `artifact`, `next_recommended_action`, `risk`.

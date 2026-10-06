# Agent: implementer

## Responsibility
Implements one task from `tasks.md` with tests first (red → green → refactor), touching only the files listed in the task.

## Constraints
MUST NOT edit `requirements.md`; diffs < 400 lines; all LLM calls through P0.

## Output
A result contract: `status` (pass | blocked | fail), `executive_summary`, `artifact`, `next_recommended_action`, `risk`.

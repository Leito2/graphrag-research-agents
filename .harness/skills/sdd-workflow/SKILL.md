# Skill: SDD workflow

## Phase DAG
`init → proposal → spec → [HUMAN GATE] → design → [HUMAN GATE] → tasks → apply → verify → archive`

## Artifact dependencies
| Phase | Needs | Produces |
|---|---|---|
| proposal | user request | `proposal.md` |
| spec | `proposal.md` | `requirements.md` (EARS) |
| design | `proposal.md`, `requirements.md` | `design.md` (+ ADRs in `decisions.json`) |
| tasks | `requirements.md`, `design.md` | `tasks.md` (atomic, < 400-line diffs, explicit validation) |
| apply | `design.md`, `tasks.md` | code + tests |
| verify | code, tests, `design.md`, `tasks.md` | `review.md` (EARS coverage 100%) |
| archive | all | copy to `.harness/memory/sessions/<task-id>/` |

## Steps
1. Read the active task in `tasks.json`; resolve the role for the phase.
2. If an input artifact is missing, return `status: blocked` with its path.
3. Produce the artifact; return the result contract. Never advance the phase yourself.

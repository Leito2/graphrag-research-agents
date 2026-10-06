# AGENTS.md — GraphRAG Multi-Agent Research System

Convention contract for every AI agent (and human) working on this repository. Read it at the start of each session.

## Project identity
- **Goal:** answer financial-crime research questions by fusing a transaction knowledge graph (from P1), private
  documents, web intelligence and visual evidence, with cited reports or an explicit "insufficient evidence".
- **Plan:** `PLAN.md` (Spanish). **Harness:** SDD with the `.harness/` control plane (PLAN §9).

## Harness conventions
1. Every feature follows `init → proposal → spec → [HUMAN GATE] → design → [HUMAN GATE] → tasks → apply → verify → archive`.
2. Specs live in `.harness/specs/<feature>/` (`proposal.md`, `requirements.md` in EARS, `design.md`, `tasks.md`, `review.md`).
3. Role contracts live in `.harness/agents/`. Agents receive only the artifacts listed in their contract (< 20% context fill).
4. Decisions persist in `.harness/memory/decisions.json` as ADRs.
5. Every phase returns a result contract: `status`, `executive_summary`, `artifact`, `next_recommended_action`, `risk`.
6. The orchestrator is deterministic: phase transitions are never decided by an LLM.

## Code conventions
- Python 3.12, type annotations on public functions, ruff + pytest; coverage ≥ 80% on `packages/` and `services/`.
- Every EARS requirement maps to a test named `test_req_<id>_*` and is listed in `review.md`.
- All LLM calls go through `llm-gateway` (P0). Secrets live in `.env` only.
- Diffs stay reviewable (< 400 lines per task).
- Never commit, push, reset or rebase unless the human supervisor asks.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Read `AGENTS.md` first** — it is the binding convention contract (hard rules on vault read-only access, no Tavily,
cloud consent, `llm-gateway`, SDD phases, test naming, diff size, and never committing/pushing unless asked).
`PLAN.md` (Spanish) is the full design; section numbers (`PLAN §x`) and ADR ids are referenced throughout the code.

## Commands

uv workspace, Python 3.12. The Makefile wraps everything (`make help`):

```bash
uv sync --all-packages --dev          # make setup
uv run pytest -q                      # make test — run from the repo root (tests read .harness/ by relative path)
uv run pytest packages/researchcore/tests/test_vault.py::test_name -q   # single test
uv run ruff check .                   # make lint (CI runs lint + tests only)
uv run ruff format .                  # make fmt
python scripts/doctor.py              # make doctor — prerequisite check
docker compose --profile core up -d   # make up PROFILE=core|full — Neo4j, Qdrant, Postgres, Redis, SearXNG, llm-gateway
```

`make index|ask|audit|eval` are placeholders that fail until later milestones (PLAN §13). Ruff line length is 110.

## Current state (M0)

Only `packages/researchcore` has code; `services/{agents,api,ingest,mcp}`, `tests/{contract,integration}` and
`eval/` are empty placeholders. Active harness task is in `.harness/tasks.json` (GRA-001, M1 vault indexing,
currently at the `spec` phase — a human gate).

## Architecture

- `researchcore/contracts.py` — Pydantic models shared by every agent: `ResearchState` flows through the graph;
  every claim in a `ResearchNote` must cite `Evidence` (with `content_hash` + `locator`, web evidence flagged
  `untrusted`). `body=None` means "insufficient evidence". `suggested_edits` are proposals, never applied.
- `researchcore/leader.py` — `next_step(state)` is the deterministic router of the runtime research loop
  (planner → fact_auditor → re-plan while open high-severity findings and `iteration < max_iterations` →
  synthesis → human approval → writer). Routing must stay pure state inspection, never an LLM call.
- `researchcore/vault.py` — pure Obsidian parser (frontmatter, wikilinks/embeds with heading/alias, tags, headings;
  code blocks stripped first) plus `LinkResolver` (exact vault path, then case-insensitive basename, like
  Obsidian). This feeds the deterministic structural graph layer (ADR-001: never LLM-extracted).
- `researchcore/graph_schema.py` — Neo4j node keys and structural relationships (mirrored in
  `infra/neo4j/constraints.cypher`), and `is_read_only()`, the first guard for Text2Cypher (no write clauses,
  must contain `LIMIT`).

Two distinct "leaders" exist: the runtime `leader.py` above, and the SDD harness Leader role
(`.harness/agents/leader.md`) that advances development phases. Both are deterministic by rule.

## SDD harness (`.harness/`)

- `tasks.json` — phase state machine (`phase_dag`, `human_gates`, `active`); validated by `tests/test_harness.py`.
- `specs/<feature>/requirements.md` — EARS requirements as `### REQ-xx <pattern>` headings; ids must be unique
  (tested). Each REQ maps to a test named `test_req_<id>_*` and must appear in that feature's `review.md`.
- `agents/*.md` — role contracts (leader, spec-author, implementer, reviewer); `skills/sdd-workflow/SKILL.md` —
  what each phase needs/produces. If an input artifact is missing, return `status: blocked`; never advance a phase
  yourself or skip a human gate.
- `memory/decisions.json` — ADRs; `memory/supervision-guide.md` — red flags (e.g. editing `requirements.md`
  during `apply`, any write path outside `RESEARCH_OUTPUT_DIR`).

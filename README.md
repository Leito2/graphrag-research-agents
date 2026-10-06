# 🕸️ GraphRAG Multi-Agent Research System

> Financial-crime research agents that fuse a **transaction knowledge graph**, private policy documents,
> **web intelligence** and **visual evidence**. A deterministic LangGraph orchestrator fans out graph, document, web,
> vision and code-verification agents; a fact-auditor resolves contradictions; every report is cited — or says
> "insufficient evidence". Built spec-first with EARS requirements and an SDD harness.
> Successor of my [multi-agent-research-system](https://github.com/Leito2/multi-agent-research-system), rebuilt around GraphRAG.

**Status:** 🟡 M0 bootstrap (contracts, deterministic Leader, graph schema, SDD harness, CI). See [`PLAN.md`](PLAN.md) (Spanish).

## TL;DR — Results at a Glance
_To be filled with measured numbers (multi-hop accuracy vs vector RAG, citation precision, rings recovered) — M8._

## Part I — The Big Picture
### 1. The Problem: relational, global and multi-source questions
### 2. Core Concepts Primer
- Knowledge graphs and GraphRAG (local vs global search, communities)
- Multi-agent roles, fan-out and fact-auditing loops
- MCP tools, sandboxed code, durable execution and human-in-the-loop
- Spec-driven development (EARS, harness, human gates)
### 3. Architecture · 4. Design Decisions · 5. Journey of an Investigation

## Part II — Components · Part III — The Graph · Part IV — The Agents
## Part V — Proof (baselines B0–B5, Microsoft GraphRAG, LightRAG, judge validation)
## Part VI — Run It Yourself

```bash
python scripts/doctor.py      # or: make doctor
uv sync --all-packages --dev  # or: make setup
uv run pytest -q              # contracts, Leader, graph schema, harness
make up                       # Neo4j, Qdrant, Postgres, Redis, llm-gateway
```

## Part VII — Reflection (what changed from the original system, limitations, future work)

## License
MIT

# 🕸️ GraphRAG Study Research Agents

> A multi-agent research system over an **Obsidian study vault** (~1,000 notes in one folder). Your wikilinks
> already form a graph: this project builds a live knowledge graph on top of them, runs GraphRAG (local and global
> search), and sends parallel agents to your notes, the web, papers, PyPI/GitHub and a code sandbox. A fact-auditor
> catches contradictions and **outdated notes**, and every result comes back as a cited, linked research note in a
> dedicated vault folder — or as "insufficient evidence". Built spec-first with EARS requirements and an SDD harness.
> Successor of my [multi-agent-research-system](https://github.com/Leito2/multi-agent-research-system): GraphRAG
> instead of vector-only RAG, and a self-hosted search stack instead of Tavily.

**Status:** 🟡 M0 bootstrap (contracts, deterministic Leader, graph schema, Obsidian parser, SDD harness, CI).
See [`PLAN.md`](PLAN.md) (Spanish).

## TL;DR — Results at a Glance
_To be filled with measured numbers (multi-hop accuracy vs vector RAG, citation precision, outdated notes detected,
held-out link recall) — M8._

## Part I — The Big Picture
### 1. The Problem: a second brain you can't query
### 2. Core Concepts Primer
- A vault as a graph; knowledge graphs and GraphRAG (local vs global search, communities)
- Multi-agent roles, fan-out and fact-auditing loops; staleness detection
- Search for agents: metasearch, crawling to Markdown, reranking (and why not Tavily)
- MCP tools, sandboxed code, durable execution and human-in-the-loop
- Spec-driven development (EARS, harness, human gates)
### Key technologies at a glance
- **GraphRAG on Neo4j** — uses the links between notes to answer questions that span several notes.
- **Multi-agent LangGraph** — specialised agents research in parallel and an auditor checks their findings.
- **MCP tools** — notes, graph, web and code are exposed as reusable tool servers.
- **Self-hosted search (SearXNG + Crawl4AI)** — web research without a paid search API.
- **SSE (Server-Sent Events)** — the progress of each agent is shown live while it works.
- **Spec-driven development** — requirements written in EARS, each one backed by a test.
### 3. Architecture · 4. Design Decisions · 5. Journey of an Investigation

## Part II — Components · Part III — The Graph · Part IV — The Agents and Research Modes
## Part V — Proof (known-ground-truth evaluation, search-stack benchmark, baselines)
## Part VI — Run It on Your Own Vault

```bash
python scripts/doctor.py      # or: make doctor
uv sync --all-packages --dev  # or: make setup
uv run pytest -q              # contracts, Leader, graph schema, Obsidian parser, harness
cp .env.example .env          # set VAULT_PATH to the folder that holds all your notes
make up                       # Neo4j, Qdrant, Postgres, Redis, SearXNG, llm-gateway
```

## Part VII — Reflection (what changed from the original system, why not Tavily, limitations)

## License
MIT

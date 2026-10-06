# Proposal: GraphRAG Study Research Agents

## Problem
A large Obsidian study vault (~1,000 notes, ~4,700 wikilinks) is hard to exploit: multi-hop questions across linked
notes, global questions (main and weak topics), outdated notes, contradictions between notes and broken code
snippets. Vector RAG and single agents fail at these, and the previous web search provider (Tavily) performed poorly.
See PLAN.md §1.

## Scope
Obsidian-aware parser with live re-indexing; knowledge graph (structural from wikilinks/tags/folders + extracted
concepts + temporal facts); GraphRAG (local, global, hybrid, Cypher); multi-agent LangGraph system with a
deterministic Leader and fact-auditing loop; self-hosted search stack (SearXNG, Crawl4AI, arXiv, OpenAlex, PyPI,
GitHub); MCP tools; sandboxed snippet execution; human-approved research notes written to one output folder;
evaluation against known ground truth.

## Out of scope
Editing existing notes automatically, syncing to Obsidian Sync/cloud, model fine-tuning, public deployment.

## Risks
Search engines blocking SearXNG, Chromium RAM, privacy of vault excerpts, accidental writes (PLAN §14).

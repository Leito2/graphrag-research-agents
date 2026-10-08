# ADR-0002: Hexagonal core, shared adapters, services as composition roots

- **Status:** accepted
- **Date:** 2026-10-08
- **Harness id:** ADR-012 (`.harness/memory/decisions.json`)

## Context
`researchcore` mixed pure domain logic with infrastructure: Neo4j Cypher (`constraints_cypher`, the Text2Cypher
guard) and filesystem reads sat next to the contracts and the Leader. The project already had to swap one external
dependency (Tavily for SearXNG, ADR-007) and keeps alternatives open for others (Neo4j vs Memgraph/FalkorDB, Qdrant
vs Chroma). Every EARS requirement also needs a `test_req_*` test, and those should run without Docker.

## Decision
One hexagon (ports and adapters), not one per service:

- **`packages/researchcore`** is the core. Its modules are named by domain (`vault/`, `graph/`, `research/`) and
  `ports.py` holds `typing.Protocol` interfaces. It depends only on pydantic and pyyaml and does no I/O.
- **`packages/researchadapters`** implements the ports (`fs_vault`, `neo4j_graph`, later Qdrant, search, LLM
  gateway). Adapters are shared because ingest, agents and MCP all reach the same stores.
- **`services/*`** are driving adapters and composition roots: they wire adapters into the core and expose it
  (FastAPI, MCP servers, the watcher, the LangGraph runtime). LangGraph is used directly in `services/agents`.
- Ports are added by the milestone that first needs them, not speculatively.
- `import-linter` enforces the rule in CI: the core may not import `researchadapters` or I/O frameworks.

## Considered options
- **Full clean architecture (entities, use cases, interface adapters, frameworks).** Rejected: the use-case layer
  would duplicate the LangGraph nodes, which are already the application flow. Hexagonal gives the same dependency
  rule with one fewer layer.
- **A hexagon per service.** Rejected: the services share one domain. Separate hexagons would duplicate the
  contracts or couple the services through each other's cores.
- **Leaving the layout as-is.** Rejected: the boundary would erode as soon as M1 adds Neo4j writes.

## Consequences
Swapping a store or search provider touches one adapter. Core tests use in-memory fakes of the ports. Moving a
module across the boundary now needs a deliberate change to the import contracts.

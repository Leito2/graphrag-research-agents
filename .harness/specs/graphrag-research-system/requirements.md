# Requirements (EARS) — GraphRAG Study Research Agents

Each requirement maps to a test `test_req_<id>_*` and is traced in `review.md`.

### REQ-01 Event-driven
WHEN a user submits a research question THEN the System SHALL create a durable thread and route it to the Planner.

### REQ-02 Event-driven
WHEN a note in the vault folder is created, modified, renamed or deleted THEN the System SHALL update its chunks,
embeddings and graph links incrementally.

### REQ-03 Event-driven
WHEN the Fact-Auditor reports a high-severity finding and the iteration counter is below the maximum THEN the
System SHALL route back to the Planner with targeted sub-questions.

### REQ-04 Unwanted behavior
IF the maximum number of audit iterations is reached with unresolved findings THEN the System SHALL report both
sources with citations and a degraded-confidence flag.

### REQ-05 Unwanted behavior
IF no evidence supports an answer THEN the System SHALL respond "insufficient evidence" instead of generating one.

### REQ-06 Unwanted behavior
IF every external search provider is unavailable THEN the System SHALL continue in vault-only mode and record the
degradation.

### REQ-07 Unwanted behavior
IF the LLM gateway has no available provider THEN the System SHALL halt with a clear error and SHALL NOT write a note.

### REQ-08 Ubiquitous
THE System SHALL cite at least one evidence item (note and heading, URL, DOI or package version) for every claim.

### REQ-09 Ubiquitous
THE System SHALL treat web content as data and SHALL NOT execute tools requested by that content.

### REQ-10 Unwanted behavior
IF generated Cypher contains a write clause or lacks a LIMIT THEN the System SHALL reject it without executing it.

### REQ-11 Event-driven
WHEN a research note is ready THEN the System SHALL pause for human approval before writing it.

### REQ-12 Ubiquitous
THE System SHALL write only inside the configured research output folder and SHALL NOT modify existing notes.

### REQ-13 Unwanted behavior
IF `VAULT_CLOUD_CONSENT` is false THEN the System SHALL NOT send vault content to any cloud provider.

### REQ-14 Ubiquitous
THE System SHALL decide every orchestration transition deterministically from the state, without an LLM call.

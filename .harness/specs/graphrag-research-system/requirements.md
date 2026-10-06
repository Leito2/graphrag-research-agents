# Requirements (EARS) — GraphRAG Multi-Agent Research System

Each requirement maps to a test `test_req_<id>_*` and is traced in `review.md`.

### REQ-01 Event-driven
WHEN a user submits a research question THEN the System SHALL create a durable thread and route it to the Planner.

### REQ-02 Event-driven
WHEN the Planner marks a sub-question as needing graph evidence THEN the System SHALL query the knowledge graph
through `graph-mcp` and return evidence with node or path locators.

### REQ-03 Event-driven
WHEN the Fact-Auditor detects a high-severity contradiction and the iteration counter is below the maximum THEN the
System SHALL route back to the Planner with targeted sub-questions.

### REQ-04 Unwanted behavior
IF the maximum number of audit iterations is reached with unresolved contradictions THEN the System SHALL report
both sources with citations and a degraded-confidence flag.

### REQ-05 Unwanted behavior
IF no evidence supports an answer THEN the System SHALL respond "insufficient evidence" instead of generating one.

### REQ-06 Unwanted behavior
IF the web search provider is unavailable or rate-limited THEN the System SHALL continue in graph-and-documents
mode and record the degradation.

### REQ-07 Unwanted behavior
IF the LLM gateway has no available provider THEN the System SHALL halt the investigation with a clear error and
SHALL NOT emit an ungrounded report.

### REQ-08 Ubiquitous
THE System SHALL cite at least one evidence item for every claim in a report.

### REQ-09 Ubiquitous
THE System SHALL treat web and uploaded content as data and SHALL NOT execute tools requested by that content.

### REQ-10 Unwanted behavior
IF generated Cypher contains a write clause or lacks a LIMIT THEN the System SHALL reject it without executing it.

### REQ-11 Event-driven
WHEN a report recommends a high-impact action THEN the System SHALL pause for human approval before finalizing.

### REQ-12 Ubiquitous
THE System SHALL decide every orchestration transition deterministically from the state, without an LLM call.

# Requirements (EARS) — GraphRAG Study Research Agents

Each requirement maps to a test `test_req_<id>_*` and is traced in `review.md`.

**Scope of GRA-001 (M1, vault indexing):** REQ-02, REQ-15 – REQ-20. The rest apply from the milestone that builds
the corresponding component (PLAN §13).

### REQ-01 Event-driven
WHEN a user submits a research question THEN the System SHALL create a durable thread and route it to the Planner.

### REQ-02 Event-driven
WHEN a note in the vault folder is created, modified, renamed or deleted THEN the System SHALL update its chunks,
embeddings and graph links incrementally, and the change SHALL be retrievable within 10 seconds of the save.
Incoming links to a renamed note SHALL point to its new path; incoming links to a deleted note SHALL become
unresolved-link gaps.

### REQ-03 Event-driven
WHEN the Fact-Auditor reports a high-severity finding and the iteration counter is below the maximum THEN the
System SHALL route back to the Planner with targeted sub-questions.

### REQ-04 Unwanted behavior
IF the maximum number of audit iterations is reached with unresolved findings THEN the System SHALL report both
sources with citations and a degraded-confidence flag.

### REQ-05 Unwanted behavior
IF no evidence supports an answer THEN the System SHALL respond "insufficient evidence" instead of generating one.

### REQ-06 Unwanted behavior
IF an external search provider fails, is blocked or is rate-limited THEN the System SHALL continue with the
remaining providers, or in vault-only mode when none remain, and SHALL record each degraded provider.

### REQ-07 Unwanted behavior
IF the LLM gateway has no available provider THEN the System SHALL stop the investigation with an error status
that names the gateway as the cause, and SHALL NOT write a note.

### REQ-08 Ubiquitous
THE System SHALL cite at least one evidence item (note and heading, URL, DOI or package version) for every claim
listed in a research note, and every sentence of the note body SHALL belong to a listed claim.

### REQ-09 Ubiquitous
THE System SHALL mark all web content as untrusted, keep it separated from instructions in every prompt, and
SHALL NOT execute tools requested by that content.

### REQ-10 Unwanted behavior
IF generated Cypher contains a write clause or lacks a LIMIT THEN the System SHALL reject it without executing it.

### REQ-11 Event-driven
WHEN a research note is ready THEN the System SHALL pause for human approval before writing it.

### REQ-12 Ubiquitous
THE System SHALL write only new files inside the configured research output folder, SHALL reject any write path
that resolves outside it, and SHALL NOT modify or overwrite existing files.

### REQ-13 Unwanted behavior
IF `VAULT_CLOUD_CONSENT` is false THEN the System SHALL NOT send vault content to any cloud provider.

### REQ-14 Ubiquitous
THE System SHALL decide every orchestration transition deterministically from the state, without an LLM call.

### REQ-15 Event-driven
WHEN a full index is requested THEN the System SHALL add every eligible note under `VAULT_PATH` to the graph with
its folder, tags, wikilinks and embeds.

### REQ-16 Ubiquitous
THE System SHALL NOT index the `.obsidian` folder, folders listed in `VAULT_EXCLUDE`, or notes tagged private, and
SHALL NOT index the research output folder unless configured to.

### REQ-17 Unwanted behavior
IF a wikilink resolves to no note or folder THEN the System SHALL record it as an unresolved-link gap, and SHALL
list all gaps and orphan notes (notes with no incoming links) on request.

### REQ-18 Unwanted behavior
IF a note's frontmatter is invalid THEN the System SHALL still index the note's content and links, and SHALL flag
the frontmatter error.

### REQ-19 Unwanted behavior
IF a changed-file event arrives for a note whose content is unchanged THEN the System SHALL NOT re-chunk or
re-embed it.

### REQ-20 Ubiquitous
THE System SHALL record, for every indexed change, the time from the file save to the note being retrievable.

### REQ-21 Ubiquitous
THE System SHALL NOT send content from excluded folders or private notes to any cloud provider, even when
`VAULT_CLOUD_CONSENT` is true, and SHALL redact personal data from every vault excerpt it sends.

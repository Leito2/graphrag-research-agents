# Tasks — GRA-001 (M1): vault indexing

**Inputs:** `requirements.md`, `design.md` (both gates approved 2026-10-08).

## Rules for every task
- Tests first (red → green → refactor), per the implementer contract. Requirement tests use the names in
  design §13.
- Touch only the files listed. If another file turns out to be necessary, stop and return `status: blocked`
  with the path instead of widening the task.
- Diff under 400 lines (the estimates below include tests). `requirements.md` is never edited during apply.
- Done means all three pass: `uv run pytest -q`, `uv run ruff check .`, `uv run lint-imports`. Docker tasks also
  pass `uv run pytest -m integration` with `docker compose up -d neo4j qdrant` running.
- Each task ends with a result contract, and the supervisor approves the commit.

Paths are shortened: `core/` = `packages/researchcore/src/researchcore/`, `core-tests/` =
`packages/researchcore/tests/`, `adapters/` = `packages/researchadapters/src/researchadapters/`,
`adapters-tests/` = `packages/researchadapters/tests/`.

## Order

```
T1 ─► T2 ─► T3 ─► T4 ─► T5 ─► T6 ─► T7 ─► T8 ─► T9
└──── pure Python, fakes only ───┘   └──── needs Docker ────┘
```

---

### T1 · Parser heading offsets, chunker, indexing policy
**REQ:** 16 (policy part) · **Docker:** no · **Estimate:** ~260 lines

Files:
- `core/vault/parser.py` (M): replace code blocks with equal-length blanks instead of deleting them; add
  `ParsedNote.heading_starts: list[int]`, the offset of each heading in the original text. `headings` keeps
  its `(level, text)` shape.
- `core/vault/chunker.py` (A): `Section`, `Chunk`, `chunk_note(parsed, text)` per design §7 (sections per
  heading, `title > heading path` prefix, 1,500-character split on blank lines, hard split as a last resort).
- `core/vault/policy.py` (A): `IndexPolicy(exclude_folders, private_tag, output_dir, index_output)` with
  `is_indexable(path, tags)`.
- `core/vault/__init__.py` (M): export the new names.
- `core-tests/test_vault.py` (M): heading offsets point at `#` in the original text, including after code blocks.
- `core-tests/test_chunker.py` (A): preamble section, nested heading paths, the split rules, stable ids.
- `core-tests/test_policy.py` (A): `test_req_16_excluded_folders_private_tag_and_output_folder_skipped`.

Validation: the three standard checks.

### T2 · Resolver: attachments, previous paths, excluded notes, link keys
**REQ:** 02 (rename rule, resolver part), 17 (excluded links are not gaps) · **Docker:** no · **Estimate:** ~180

Files:
- `core/vault/resolver.py` (M): constructor gains `attachments`, `excluded` and `previous` (old key → current
  path); a `classify(target, source)` returning note, folder, attachment, excluded or missing; and
  `link_key(target, source) -> (target_key, target_name)`, the normalization stored on `LINKS_TO`. An exact path
  wins over the previous-path map. The resolver stays immutable; the indexer rebuilds it on structural changes
  (about 1 ms for 1,000 paths).
- `core-tests/test_resolver.py` (A): the existing resolver tests move here from `test_vault.py`, plus
  previous-path fallback, exact path beating the fallback, excluded targets, attachments by basename.
- `core-tests/test_vault.py` (M): drop the moved tests.

### T3 · Ports, indexing model, graph delta, in-memory fakes
**REQ:** groundwork for 02, 15–20 · **Docker:** no · **Estimate:** ~370

Files:
- `core/ports.py` (M): `VaultReader.mtime`; new `GraphStore`, `VectorStore`, `Embedder`, `Clock` per design §4;
  roadmap docstring updated (VectorStore now M1).
- `core/indexing/__init__.py` (A), `core/indexing/model.py` (A): `NoteGraph`, `ResolvedLink`, `EmbeddedChunk`,
  `Hit`, `Gap`.
- `core/indexing/delta.py` (A): pure `build_note_graph(parsed, text, resolver, hash, mtime) -> NoteGraph`.
- `core/graph/schema.py` (M): `LINKS_TO` may target `Folder`.
- `core/testing/__init__.py` (A), `core/testing/fakes.py` (A): in-memory `FakeVault`, `FakeGraphStore`,
  `FakeVectorStore`, `FakeEmbedder` (deterministic vectors, call counter), `FakeClock`. They live in the package
  so the contract tests in T6 and T7 can import them.
- `adapters/fs_vault.py` (M): `FsVault.mtime`.
- `core-tests/test_delta.py` (A), `core-tests/test_graph_schema.py` (M), `adapters-tests/test_fs_vault.py` (M).

### T4 · Indexer: full index, single-note changes, relinking
**REQ:** 02 (create, modify, delete), 15, 18, 19 · **Docker:** no · **Estimate:** ~380

Files:
- `core/indexing/events.py` (A): `VaultEvent`, `IndexReport`.
- `core/indexing/indexer.py` (A): `Indexer(vault, graph, vectors, embedder, clock, policy)` with `full_index()`,
  `apply(event)` for created, modified and deleted notes, the write order from design §6.2, and `relink` for the
  notes whose links a create or delete changes (design §6.3).
- `core-tests/test_indexer.py` (A): `test_req_02_modified_note_updates_chunks_and_links`,
  `test_req_02_delete_turns_incoming_links_into_gaps`, `test_req_02_new_note_wins_basename_resolution`,
  `test_req_15_full_index_adds_every_eligible_note`, `test_req_18_invalid_frontmatter_still_indexed_and_flagged`,
  `test_req_19_unchanged_content_is_not_reembedded`, `test_req_19_relink_does_not_reembed`.

### T5 · Indexer: renames, privacy changes, freshness, reconcile, report
**REQ:** 02 (rename), 16 (note becoming private), 17, 20 · **Docker:** no · **Estimate:** ~300

Files:
- `core/indexing/indexer.py` (M): moved events (single notes and folders) with `record_move`; notes that become
  private or excluded handled as deletes and the reverse as creates; freshness records; `reconcile()`;
  `report()` with gaps, orphans, frontmatter errors, unreadable files and freshness p50/p95.
- `core-tests/test_indexer_structure.py` (A): `test_req_02_rename_keeps_incoming_links`,
  `test_req_16_note_becoming_private_is_removed`, `test_req_20_freshness_recorded_per_change`, reconcile after a
  simulated crash between the two stores, report contents.

### T6 · Neo4j adapter and the GraphStore contract
**REQ:** 17 (contract level), plus real coverage for 02 and 15 · **Docker:** yes · **Estimate:** ~390

Files:
- `adapters/neo4j_graph.py` (M): `Neo4jGraphStore` implementing `GraphStore` (`UNWIND` batches, `ensure_schema`
  from `constraints_cypher()`, `MissingNote` cleanup, gap and orphan queries).
- `packages/researchadapters/pyproject.toml` (M): `neo4j` driver.
- `pyproject.toml` (M): register the `integration` marker; `addopts = -m "not integration"` so the default run
  stays Docker-free.
- `tests/contract/test_graph_store_contract.py` (A): one suite parametrized over `FakeGraphStore` and
  `Neo4jGraphStore` (the latter marked `integration`), including `test_req_17_unresolved_links_become_gaps`
  and `test_req_17_orphans_listed`.
- `docker-compose.yml` (M): pin the `neo4j` image to an exact version.

### T7 · Qdrant adapter, e5 embedder, VectorStore contract
**REQ:** 02 (retrievable) · **Docker:** yes · **Estimate:** ~330

Files:
- `adapters/qdrant_vectors.py` (A): `QdrantVectorStore` (UUID5 point ids, `note_path` payload index,
  delete-by-note with `except_hash`).
- `adapters/e5_embedder.py` (A): `E5Embedder` per design §8 (fastembed custom model, `passage: ` and `query: `
  prefixes); falls back to `onnxruntime` and `tokenizers` only if the custom model fails to load.
- `packages/researchadapters/pyproject.toml` (M): `qdrant-client`, `fastembed`.
- `tests/contract/test_vector_store_contract.py` (A): parametrized over `FakeVectorStore` and
  `QdrantVectorStore`.
- `adapters-tests/test_e5_embedder.py` (A, `integration`): dimension 384, prefixes applied, a Spanish and an
  English paraphrase rank above an unrelated text, and peak process memory written to the test output.
- `docker-compose.yml` (M): pin the `qdrant` image.

### T8 · The `ingest` service
**REQ:** 02 (watcher), 16 (configuration) · **Docker:** to run end to end · **Estimate:** ~380

Files:
- `services/ingest/pyproject.toml` (A); `services/ingest/src/ingest/__init__.py`, `__main__.py` (CLI with
  `full`, `watch`, `report`), `settings.py` (env), `wiring.py` (composition root), `watcher.py` (watchdog, 500 ms
  debounce per path, coalescing, `native` or `polling` observer) (A).
- `services/ingest/tests/test_watcher.py` (A): temp-file-and-rename save becomes one event; bursts coalesce;
  moved events keep both paths.
- `pyproject.toml` (M): workspace member, `ingest` dependency, test path, import-linter contract that
  `researchcore` and `researchadapters` do not import `ingest`.
- `Makefile` (M): `index` runs `uv run python -m ingest full`; new `watch` and `report` targets.
- `.env.example` (M): `INDEX_RESEARCH_OUTPUT`, `PRIVATE_TAG`, `INGEST_OBSERVER`, `EMBEDDING_MODEL`.

Validation also includes a manual run: `make index` on the real vault, then `make report`, with the counts
compared against PLAN §3.5 (991 notes, 4,482 links).

### T9 · Integration CI, freshness test, coverage gate
**REQ:** 02 (10-second bound), 15 (end to end) · **Docker:** yes · **Estimate:** ~220

Files:
- `.github/workflows/ci.yml` (M): `integration` job with Neo4j and Qdrant service containers running
  `pytest -m integration`; the unit job enforces coverage of at least 80% on `packages/` and `services/`.
- `tests/integration/test_req_02_freshness.py` (A): `test_req_02_saved_note_retrievable_within_10s`, a real
  watcher on a temp vault.
- `tests/integration/test_req_15_full_index.py` (A): full index of a fixture vault into both stores.
- `CLAUDE.md` (M): integration-test and `ingest` commands.

---

After T9: **verify** writes `review.md` (every requirement → test → result), then **archive**.

# Design — GRA-001 (M1): vault indexing

**Inputs:** `proposal.md`, `requirements.md` (spec gate approved 2026-10-08). **Covers:** REQ-02, REQ-15 – REQ-20.
**Architecture:** hexagonal (ADR-012). New decisions are recorded as ADR-013 – ADR-015 (status `proposed` until the
design gate).

## 1. Scope

In scope: heading-aware chunking, local embeddings, the structural graph in Neo4j, chunk vectors in Qdrant, a live
watcher with incremental updates, startup reconciliation, the gaps/orphans report and freshness measurement.

Out of scope, and why:
- **Evaluation snapshot and sets v0** (listed under M1 in PLAN §13) have no requirement in the approved spec.
  They become **GRA-002**, with their own requirements, so this task stays reviewable.
- Concepts, temporal facts and communities (M3–M4); note language detection (`Note.lang` stays null until
  GRA-002 needs it for per-language sets); the Text2Cypher guard fix (REQ-10, M3).

## 2. Shape

```
                driving side                         core (researchcore)                     driven side
 watchdog observer ─► services/ingest ──calls──► indexing.Indexer ──ports──► VaultReader  ◄─ researchadapters.fs_vault
 CLI (full/watch/report) ┘   (composition root)   vault.parser / resolver     GraphStore   ◄─ researchadapters.neo4j_graph
                                                  vault.chunker / policy      VectorStore  ◄─ researchadapters.qdrant_vectors
                                                  indexing.delta (pure)       Embedder     ◄─ researchadapters.e5_embedder
                                                                              Clock        ◄─ system clock (fake in tests)
```

The `Indexer` is an application service in the core: it decides *what* changes, through ports only, so every
indexing requirement except the 10-second bound is unit-tested with in-memory fakes.

## 3. Modules

| Location | Module | Responsibility |
|---|---|---|
| `researchcore/vault/` | `parser.py` (changed) | Mask code blocks with equal-length blanks instead of deleting them, and return heading **offsets**, so sections map back to the original text. |
| | `resolver.py` (changed) | Also resolve attachments (any file type) and fall back to a **previous-path map** for renamed notes (§6.3). Track excluded paths so links to them are not reported as gaps. |
| | `chunker.py` (new) | `Section`s per heading and `Chunk`s per section (§7). |
| | `policy.py` (new) | `is_indexable(path, tags, config)` for REQ-16. |
| `researchcore/indexing/` (new) | `events.py` | `VaultEvent` (created, modified, moved, deleted), `IndexReport`. |
| | `delta.py` | Pure: `ParsedNote` + resolver → `NoteGraph` (note, folder chain, tags, sections, chunks, links, embeds). |
| | `indexer.py` | `Indexer.full_index()`, `apply(event)`, `reconcile()`, `report()`. |
| `researchcore/ports.py` | | Adds `GraphStore`, `VectorStore`, `Embedder`, `Clock` (§4). |
| `researchcore/graph/schema.py` | | `LINKS_TO` may also target `Folder` (11% of the vault's links, PLAN §3.5). |
| `researchadapters/` | `neo4j_graph.py`, `qdrant_vectors.py`, `e5_embedder.py` | Real adapters (§5, §8). `fs_vault` gains `mtime(path)`. |
| `services/ingest/` (new package `ingest`) | `__main__.py`, `watcher.py`, `settings.py` | CLI `python -m ingest` with `full`, `watch` and `report`, debounced observer, env settings. `make index` runs `full`. |

`import-linter` gets a third contract: `researchcore` and `researchadapters` may not import `ingest`.

## 4. Ports

```python
class GraphStore(Protocol):
    def ensure_schema(self) -> None
    def note_hashes(self) -> dict[str, str]                       # path -> content hash (the commit marker)
    def previous_paths(self) -> dict[str, str]                    # old key -> current path
    def upsert_note(self, graph: NoteGraph) -> None               # one transaction; sets Note.hash last
    def relink(self, path: str, links: list[ResolvedLink]) -> None  # links only, no chunks (REQ-19)
    def delete_note(self, path: str) -> None
    def record_move(self, old: str, new: str) -> None
    def sources_linking(self, keys: set[str], names: set[str]) -> set[str]
    def gaps(self) -> list[Gap]                                   # MissingNote targets with incoming counts
    def orphans(self) -> list[str]                                # notes with no incoming LINKS_TO/EMBEDS

class VectorStore(Protocol):
    def ensure_collection(self, dim: int) -> None
    def upsert(self, chunks: list[EmbeddedChunk]) -> None
    def delete_note(self, path: str, except_hash: str | None = None) -> None
    def search(self, vector: list[float], k: int) -> list[Hit]

class Embedder(Protocol):
    dim: int
    def embed_passages(self, texts: list[str]) -> list[list[float]]
    def embed_query(self, text: str) -> list[float]
```

`VectorStore` moves from M2 to M1 in the `ports.py` roadmap, because REQ-02 requires embeddings.

## 5. Data model

**Neo4j** (constraints come from `constraints_cypher()`, applied idempotently by `ensure_schema`):
- `Note {path, title, hash, mtime, frontmatter_error, previous_paths}`; `Folder {path}`; `Tag {name}`;
  `Section {id, note_path, heading_path}`; `Chunk {id, note_path, hash}`; `MissingNote {target}`;
  `Attachment {path}`.
- `LINKS_TO {alias, heading, target_key, target_name}` → `Note | Folder | MissingNote`. `target_key` is the
  link target made absolute and lower-cased without `.md`; `target_name` is its basename. Both drive §6.3.
- Writes use `UNWIND` batches (500 notes per transaction in a full index). `MissingNote`s left without incoming
  links are deleted at the end of each transaction.

**Qdrant:** collection `chunks`, cosine distance, `dim` from the embedder. Point id = UUID5 of the chunk id.
Payload: `note_path`, `section_id`, `heading_path`, `hash`, with a payload index on `note_path` for
delete-by-note.

## 6. Flows

### 6.1 Full index (REQ-15, REQ-16, REQ-18)
List notes → read and SHA-256 each → parse → apply the policy (excluded notes go to the resolver's excluded set
only) → build one resolver from all paths → `delta` per note → embed in batches of 64 → vector upserts → graph
upserts. Unreadable or non-UTF-8 files are reported and skipped; they never stop the run. Frontmatter errors are
stored on the note and counted in the report.

### 6.2 One changed note (REQ-02, REQ-19, REQ-20)
1. The watcher debounces events per path (500 ms) and coalesces them, so an editor's temp-file-and-rename save
   becomes one event. A single worker applies events in order.
2. Read and hash. **If the hash equals `Note.hash`, stop** (REQ-19): no parse, no embedding.
3. Parse and apply the policy. A note that became private or excluded is handled as a delete; one that stopped
   being private is handled as a create.
4. Chunk, embed, upsert vectors (chunk ids include the new hash), then upsert the graph in one transaction that
   writes `Note.hash` last, then delete the note's vectors with any other hash.
5. Record freshness = time after step 4 − file `mtime` (§10).

**Write order is the consistency mechanism (ADR-014):** `Note.hash` in Neo4j is the commit marker. A crash between
the stores leaves either a stale hash (reindexed on reconcile) or extra vectors with the wrong hash (purged on
reconcile). There is no cross-store transaction.

### 6.3 Create, delete and rename (REQ-02 link rules)
These change what *other* notes' links resolve to, including basename resolution, where a new shallower note can
win. After updating the resolver, the indexer asks `sources_linking(keys, names)` for every note whose stored
`target_key` or `target_name` matches the changed path, and **relinks** them. Relinking re-parses the source and
rewrites only its links, without re-chunking or re-embedding, so REQ-19 still holds.
- **Delete:** the note's subgraph and vectors are removed; relinked sources now point to `MissingNote` gaps.
- **Rename/move:** `record_move(old, new)` adds the old key to the resolver's previous-path map, so links that
  still use the old name keep pointing to the note (REQ-02). This holds even when the note is renamed outside
  Obsidian. An exact path always wins over the map, so a new note created at the old path takes its links back.
  Folder moves expand into one move per note.

### 6.4 Startup reconciliation
`watch` first runs `reconcile()`: compare file hashes with `note_hashes()`, apply the differences as events, and
purge vectors whose hash differs from the graph. This covers edits made while the watcher was down and partial
writes (§6.2).

### 6.5 Report (REQ-17, REQ-18, REQ-20)
`python -m ingest report [--json PATH]` lists gaps (target, incoming count, linking notes), orphans, frontmatter
errors, unreadable files, and freshness p50/p95. It writes to stdout or a path outside the vault, never into the
vault (REQ-12).

## 7. Chunking
One `Section` per heading (the preamble before the first heading is a section titled after the note). Its id is
`path#H1 > H2 > …`. Each section becomes one chunk prefixed with `title > heading path`, unless it exceeds
1,500 characters. Then it splits on blank lines into chunks of at most 1,500 characters, and hard-splits a single
oversized paragraph. That keeps every chunk under the embedder's 512-token limit. Code blocks stay in the chunk
text. The inherited 512/64 recursive splitter is the M2 baseline (PLAN §3.2), not part of this task.

## 8. Embeddings (ADR-015)
`intfloat/multilingual-e5-small`, 384 dimensions, MIT license, via its official ONNX export (`onnx/model.onnx` in
the Hugging Face repo), loaded as a fastembed custom model with mean pooling and normalization. fastembed 0.9.0
ships only the large e5 variant (2.24 GB), which does not fit the 8 GB budget. The adapter adds e5's required
prefixes (`passage: ` for chunks, `query: ` for queries). Embeddings run locally and are not LLM calls, so no vault
text leaves the machine for indexing (REQ-13, REQ-21). The int8 export targets AVX-512 VNNI CPUs only, so fp32 is
the default.

## 9. Where the watcher runs (ADR-013)
The vault lives on the Windows filesystem. File-change notifications from a Windows bind mount do not reliably
reach Linux containers, so the default is to run `ingest` **on the host** (`uv run python -m ingest watch`), using
watchdog's native observer and the Dockerized Neo4j and Qdrant through `localhost`. The same package also runs in a
container: on a Linux host the native observer works there, and `INGEST_OBSERVER=polling` covers bind mounts
without notifications. On the host, read-only access is enforced by code: ingest only reads through `VaultReader`,
which has no write method.

## 10. Freshness (REQ-02, REQ-20)
"Retrievable" means the note's current hash is committed in the graph and its chunks are searchable. Each applied
event appends `{path, mtime, committed_at, seconds}` to `metrics.jsonl` (the inherited MLflow-fallback format, with
no note content). Budget for one note: 0.5 s debounce + parse < 50 ms + embedding about 20 chunks ≈ 1 s on CPU +
two upserts < 0.5 s, about 2 s against the 10-second requirement. Large notes are the risk, and `report` exposes
p95.

## 11. Configuration
Existing: `VAULT_PATH`, `VAULT_EXCLUDE`, `RESEARCH_OUTPUT_DIR`, `NEO4J_*`, `QDRANT_URL`. New in `.env.example`:
`INDEX_RESEARCH_OUTPUT=false` (REQ-16), `PRIVATE_TAG=private`, `INGEST_OBSERVER=native|polling`,
`EMBEDDING_MODEL=intfloat/multilingual-e5-small`. The `neo4j` and `qdrant` images get pinned to exact versions in
this task (`docker-compose.yml` already flags it).

## 12. Alternatives considered

| Decision | Chosen | Rejected and why |
|---|---|---|
| Watcher runtime (ADR-013) | Host process with the native observer; polling as an opt-in | **Container with native observer:** events from Windows bind mounts are unreliable. **Polling by default:** stat-scanning about 1,000 files over the mount every cycle costs CPU and latency against the 10 s budget. **Obsidian plugin pushing events:** ties indexing to Obsidian running and adds a TypeScript codebase. |
| Vector store | Qdrant behind `VectorStore` (ADR-INH-004) | **Neo4j's native vector index only:** one store would remove the dual-write problem, but M4's hybrid search needs Qdrant's sparse and dense fusion. The port keeps this swap to one adapter if M4 changes course. |
| Store consistency (ADR-014) | Ordered writes + `Note.hash` commit marker + reconcile | **Outbox table:** needs a third store or Neo4j-side queue for a single-user tool. **Writing the graph first:** a crash would mark a note current while its vectors are missing, which is invisible to reconcile. |
| Embedding model (ADR-015) | multilingual-e5-small via its ONNX export | **multilingual-e5-large:** 2.24 GB. **paraphrase-multilingual-MiniLM-L12-v2** (built into fastembed, 0.22 GB): the fallback if e5-small misbehaves, but it departs from the accepted ADR-INH-005. **bge-small-en-v1.5:** English only, and the vault mixes English and Spanish; kept as an M2 comparison. |
| Rename handling | Previous-path map in the resolver | **Re-resolve from link text only:** links not rewritten by Obsidian would turn into gaps, breaking REQ-02. **Rewrite the linking notes:** violates the read-only vault (REQ-12). |

## 13. Requirement → test traceability

| REQ | Test (planned) | Level |
|---|---|---|
| 02 | `test_req_02_modified_note_updates_chunks_and_links`, `_rename_keeps_incoming_links`, `_delete_turns_incoming_links_into_gaps`, `_new_note_wins_basename_resolution` | unit (fakes) |
| 02 | `test_req_02_saved_note_retrievable_within_10s` | integration (watcher + Neo4j + Qdrant) |
| 15 | `test_req_15_full_index_adds_every_eligible_note` | unit + integration |
| 16 | `test_req_16_excluded_folders_private_tag_and_output_folder_skipped`, `_note_becoming_private_is_removed` | unit |
| 17 | `test_req_17_unresolved_links_become_gaps`, `_orphans_listed` | contract (fake and Neo4j run the same test) |
| 18 | `test_req_18_invalid_frontmatter_still_indexed_and_flagged` | unit |
| 19 | `test_req_19_unchanged_content_is_not_reembedded`, `_relink_does_not_reembed` | unit (embedder call count) |
| 20 | `test_req_20_freshness_recorded_per_change` | unit (fake clock) |

CI gains an `integration` job with Neo4j and Qdrant service containers running `pytest -m integration`. The
`tests/contract` suite runs each port test against the fake and the real adapter, so the fakes cannot drift.

## 14. Risks and open questions
- **Memory:** the fp32 e5-small model is about 470 MB on disk, and the ingest process may exceed its share of the
  800 MB PLAN §11 budget for Python services. It gets measured in apply; the MiniLM fallback is about half the size.
- **fastembed custom-model loading** of the e5 ONNX export is unverified in this repo. If it fails, the adapter
  uses `onnxruntime` and `tokenizers` directly, behind the same `Embedder` port.
- **Huge notes** can push a single event past the freshness budget; p95 in the report will show it.
- **Windows long paths** (> 260 characters) are already handled in `fs_vault`; the watcher must emit paths in the
  same form.

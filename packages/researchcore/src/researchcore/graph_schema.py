"""Knowledge-graph schema (PLAN §4.1): the structural layer mirrors the Obsidian vault."""
NODE_KEYS: dict[str, str] = {
    "Note": "path", "MissingNote": "target", "Folder": "path", "Tag": "name", "Section": "id", "Chunk": "id",
    "Attachment": "path", "Concept": "id", "Fact": "id", "Community": "id", "Finding": "id", "Source": "url",
}

# Deterministic relationships produced by the vault parser (ADR-1) — no LLM involved.
STRUCTURAL_RELS: dict[str, tuple[str, str]] = {
    "LINKS_TO": ("Note", "Note|MissingNote"),
    "IN_FOLDER": ("Note|Folder", "Folder"),
    "TAGGED": ("Note", "Tag"),
    "HAS_SECTION": ("Note", "Section"),
    "HAS_CHUNK": ("Section", "Chunk"),
    "EMBEDS": ("Note", "Attachment|Note"),
}

WRITE_CLAUSES = ("CREATE", "MERGE", "DELETE", "DETACH", "SET", "REMOVE", "DROP", "LOAD CSV", "CALL DBMS")


def constraints_cypher() -> list[str]:
    return [
        f"CREATE CONSTRAINT {label.lower()}_{key} IF NOT EXISTS FOR (n:{label}) REQUIRE n.{key} IS UNIQUE"
        for label, key in NODE_KEYS.items()
    ]


def is_read_only(cypher: str) -> bool:
    """First guard for Text2Cypher (PLAN §4.3); the read-only DB role is the second one."""
    upper = " ".join(cypher.upper().split())
    return not any(clause in upper for clause in WRITE_CLAUSES) and " LIMIT " in f" {upper} "

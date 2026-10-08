"""Knowledge-graph schema (PLAN §4.1): the structural layer mirrors the Obsidian vault."""
NODE_KEYS: dict[str, str] = {
    "Note": "path", "MissingNote": "target", "Folder": "path", "Tag": "name", "Section": "id", "Chunk": "id",
    "Attachment": "path", "Concept": "id", "Fact": "id", "Community": "id", "Finding": "id", "Source": "url",
}

# Deterministic relationships produced by the vault parser (ADR-001) — no LLM involved.
STRUCTURAL_RELS: dict[str, tuple[str, str]] = {
    "LINKS_TO": ("Note", "Note|MissingNote"),
    "IN_FOLDER": ("Note|Folder", "Folder"),
    "TAGGED": ("Note", "Tag"),
    "HAS_SECTION": ("Note", "Section"),
    "HAS_CHUNK": ("Section", "Chunk"),
    "EMBEDS": ("Note", "Attachment|Note"),
}

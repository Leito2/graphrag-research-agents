"""The vault as a source: Obsidian parsing and link resolution, pure functions over text (PLAN §3.1)."""
from researchcore.vault.parser import Link, ParsedNote, parse_note
from researchcore.vault.resolver import LinkResolver

__all__ = ["Link", "LinkResolver", "ParsedNote", "parse_note"]

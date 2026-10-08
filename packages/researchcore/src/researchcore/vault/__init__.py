"""The vault as a source: Obsidian parsing, link resolution, chunking and the indexing policy (PLAN §3)."""
from researchcore.vault.chunker import Chunk, Section, chunk_note
from researchcore.vault.parser import Link, ParsedNote, parse_note
from researchcore.vault.policy import IndexPolicy
from researchcore.vault.resolver import LinkResolver

__all__ = ["Chunk", "IndexPolicy", "Link", "LinkResolver", "ParsedNote", "Section", "chunk_note",
           "parse_note"]

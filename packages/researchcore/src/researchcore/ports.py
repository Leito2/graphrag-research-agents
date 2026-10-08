"""Ports (ADR-012): the interfaces the core needs from the outside world. Adapters live in `researchadapters`.

A port is added by the milestone that first needs it, not speculatively: GraphStore (M1), VectorStore and LLM
(M2), NoteWriter (M5), WebSearch and ScholarSearch (M6), Sandbox (M7).
"""
from typing import Protocol


class VaultReader(Protocol):
    """Read-only access to the Obsidian vault (ADR-003)."""

    def list_notes(self) -> list[str]:
        """Vault-relative POSIX paths of every indexed note."""
        ...

    def read(self, rel_path: str) -> str: ...

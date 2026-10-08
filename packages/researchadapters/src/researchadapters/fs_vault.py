"""Filesystem adapter for the VaultReader port: the only code that touches the vault on disk.

The vault is read-only (ADR-003); writes to RESEARCH_OUTPUT_DIR get their own adapter (M5).
"""
import os
from pathlib import Path, PurePosixPath


def read_note(root: Path, rel_path: str) -> str:
    """Read a note; on Windows use the extended-length prefix (vault paths often exceed 260 chars)."""
    path = (root / rel_path).resolve()
    prefix = "\\\\?\\"                     # the Windows extended-length path prefix: \\?\
    if os.name == "nt" and not str(path).startswith(prefix):
        path = Path(prefix + str(path))
    return path.read_text(encoding="utf-8")


def iter_vault(root: Path, exclude: tuple[str, ...] = (".obsidian",)) -> list[str]:
    """Vault-relative POSIX paths of every Markdown note under one folder (recursive)."""
    notes = []
    for p in root.rglob("*.md"):
        rel = p.relative_to(root).as_posix()
        if not any(part in exclude for part in PurePosixPath(rel).parts):
            notes.append(rel)
    return sorted(notes)


class FsVault:
    """VaultReader over one folder on disk."""

    def __init__(self, root: Path, exclude: tuple[str, ...] = (".obsidian",)):
        self.root, self.exclude = root, exclude

    def list_notes(self) -> list[str]:
        return iter_vault(self.root, self.exclude)

    def read(self, rel_path: str) -> str:
        return read_note(self.root, rel_path)

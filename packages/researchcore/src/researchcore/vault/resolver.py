"""Wikilink resolution against the set of note paths, the way Obsidian does it (PLAN §3.1)."""
import posixpath
from pathlib import PurePosixPath


class LinkResolver:
    """Resolve wikilinks like Obsidian: exact vault path first, then basename (case-insensitive)."""

    def __init__(self, note_paths: list[str]):
        self._by_path = {self._key(p): p for p in note_paths}
        # Every ancestor folder: the vault links course folders directly ("[[06 - LLMs/19 - LiteLLM]]").
        self._folders = {str(parent).lower(): str(parent)
                         for p in note_paths for parent in PurePosixPath(p).parents if str(parent) != "."}
        self._by_name: dict[str, list[str]] = {}
        for p in sorted(note_paths, key=lambda p: (p.count("/"), p)):   # shortest path wins, like Obsidian
            self._by_name.setdefault(PurePosixPath(p).stem.lower(), []).append(p)

    @staticmethod
    def _key(path: str) -> str:
        return path.removesuffix(".md").lower()      # not with_suffix(): "LangGraph v0.2" keeps its dot

    @staticmethod
    def _absolute(target: str, source: str | None) -> str:
        """Relative links ("../Course/Note.md") are resolved against the linking note's folder."""
        if source and target.startswith(("./", "../")):
            joined = posixpath.normpath(posixpath.join(posixpath.dirname(source), target))
            return "" if joined.startswith("..") else joined
        return target

    def resolve(self, target: str, source: str | None = None) -> str | None:
        target = self._absolute(target, source)
        if not target:
            return None
        clean = target.removesuffix(".md")
        if hit := self._by_path.get(self._key(clean)):
            return hit
        if "/" not in clean and (candidates := self._by_name.get(clean.lower())):
            return candidates[0]
        return None

    def resolve_folder(self, target: str, source: str | None = None) -> str | None:
        """Folder targets become links to a Folder node instead of MissingNote gaps."""
        target = self._absolute(target, source)
        return self._folders.get(target.strip("/").lower()) if target else None

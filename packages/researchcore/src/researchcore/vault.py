"""Obsidian vault parsing (PLAN §3.1): frontmatter, wikilinks, embeds, tags and headings.

Pure functions, no I/O beyond reading a file, so the structural graph layer is deterministic and testable.
"""
import os
import posixpath
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

import yaml

_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
_FENCE = re.compile(r"^(```|~~~).*?^\1", re.DOTALL | re.MULTILINE)
_INLINE_CODE = re.compile(r"`[^`\n]*`")
_LINK = re.compile(r"(!?)\[\[([^\]\n]+?)\]\]")
_TAG = re.compile(r"(?<![\w/#&])#([A-Za-z_][\w/-]*)")
_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Link:
    target: str                 # as written, without alias/heading ("folder/Note" or "Note")
    heading: str | None = None
    alias: str | None = None
    embed: bool = False


@dataclass
class ParsedNote:
    path: str                   # vault-relative POSIX path
    title: str
    frontmatter: dict = field(default_factory=dict)
    frontmatter_error: bool = False     # invalid YAML is reported, never fatal
    links: list[Link] = field(default_factory=list)
    tags: set[str] = field(default_factory=set)
    headings: list[tuple[int, str]] = field(default_factory=list)
    code_blocks: int = 0


def _strip_code(body: str) -> tuple[str, int]:
    blocks = len(_FENCE.findall(body))
    return _INLINE_CODE.sub("", _FENCE.sub("", body)), blocks


def parse_note(text: str, rel_path: str) -> ParsedNote:
    frontmatter: dict = {}
    fm_error = False
    body = text
    if m := _FRONTMATTER.match(text):
        try:
            loaded = yaml.safe_load(m.group(1))
        except yaml.YAMLError:
            loaded, fm_error = None, True
        frontmatter = loaded if isinstance(loaded, dict) else {}
        body = text[m.end():]

    prose, n_blocks = _strip_code(body)
    links = []
    for bang, inner in _LINK.findall(prose):
        target, _, alias = inner.partition("|")
        target, _, heading = target.partition("#")
        links.append(Link(target=target.strip(), heading=heading.strip() or None,
                          alias=alias.strip() or None, embed=bang == "!"))

    headings = [(len(h), t) for h, t in _HEADING.findall(prose)]
    prose_without_headings = _HEADING.sub("", prose)
    tags = {t for t in _TAG.findall(prose_without_headings)}
    fm_tags = frontmatter.get("tags") or []
    tags |= {str(t).lstrip("#") for t in ([fm_tags] if isinstance(fm_tags, str) else fm_tags)}

    path = PurePosixPath(rel_path)
    return ParsedNote(path=str(path), title=path.stem, frontmatter=frontmatter, frontmatter_error=fm_error,
                      links=links, tags=tags, headings=headings, code_blocks=n_blocks)


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

"""Obsidian note parsing (PLAN §3.1): frontmatter, wikilinks, embeds, tags and headings.

Pure functions over text, so the structural graph layer is deterministic and testable (ADR-001).
"""
import re
from dataclasses import dataclass, field
from pathlib import PurePosixPath

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

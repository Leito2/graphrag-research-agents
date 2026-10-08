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
_HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$", re.MULTILINE)


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
    heading_starts: list[int] = field(default_factory=list)    # offset of each heading in the original text
    body_start: int = 0                                         # offset just after the frontmatter
    code_blocks: int = 0


def _blank(m: re.Match) -> str:
    return re.sub(r"[^\n]", " ", m.group(0))


def _mask_code(body: str) -> tuple[str, int]:
    """Blank out code with equal-length whitespace, so offsets in the result are offsets in `body`."""
    blocks = len(_FENCE.findall(body))
    return _INLINE_CODE.sub(_blank, _FENCE.sub(_blank, body)), blocks


def parse_note(text: str, rel_path: str) -> ParsedNote:
    frontmatter: dict = {}
    fm_error = False
    body, body_start = text, 0
    if m := _FRONTMATTER.match(text):
        try:
            loaded = yaml.safe_load(m.group(1))
        except yaml.YAMLError:
            loaded, fm_error = None, True
        frontmatter = loaded if isinstance(loaded, dict) else {}
        body, body_start = text[m.end():], m.end()

    prose, n_blocks = _mask_code(body)
    links = []
    for bang, inner in _LINK.findall(prose):
        target, _, alias = inner.partition("|")
        target, _, heading = target.partition("#")
        links.append(Link(target=target.strip(), heading=heading.strip() or None,
                          alias=alias.strip() or None, embed=bang == "!"))

    heading_matches = list(_HEADING.finditer(prose))
    headings = [(len(h.group(1)), h.group(2)) for h in heading_matches]
    prose_without_headings = _HEADING.sub("", prose)
    tags = {t for t in _TAG.findall(prose_without_headings)}
    fm_tags = frontmatter.get("tags") or []
    tags |= {str(t).lstrip("#") for t in ([fm_tags] if isinstance(fm_tags, str) else fm_tags)}

    path = PurePosixPath(rel_path)
    return ParsedNote(path=str(path), title=path.stem, frontmatter=frontmatter, frontmatter_error=fm_error,
                      links=links, tags=tags, headings=headings,
                      heading_starts=[body_start + h.start() for h in heading_matches], body_start=body_start,
                      code_blocks=n_blocks)

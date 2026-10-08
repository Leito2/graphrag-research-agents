"""Heading-aware chunking (PLAN §3.2, design §7): one Section per heading, chunks prefixed with context."""
import re
from dataclasses import dataclass

from researchcore.vault.parser import ParsedNote

MAX_CHARS = 1500                       # keeps every chunk under the embedder's 512-token limit
_PARAGRAPH_BREAK = re.compile(r"\n[ \t]*\n")


@dataclass(frozen=True)
class Chunk:
    id: str                            # "<section id>#<index>"
    section_id: str
    text: str                          # "<title> > <heading path>", a blank line, then the content


@dataclass(frozen=True)
class Section:
    id: str                            # "<note path>#<heading path>", "~2", "~3"... for repeated headings
    heading_path: str                  # "H1 > H2"; "" for the preamble before the first heading
    level: int                         # 0 for the preamble
    chunks: tuple[Chunk, ...]


def _pieces(body: str, budget: int) -> list[str]:
    """Paragraphs packed up to `budget` characters; a paragraph longer than that is hard-split."""
    pieces: list[str] = []
    current = ""
    for paragraph in (p.strip() for p in _PARAGRAPH_BREAK.split(body)):
        if not paragraph:
            continue
        if len(paragraph) > budget:
            if current:
                pieces.append(current)
                current = ""
            pieces += [paragraph[i:i + budget] for i in range(0, len(paragraph), budget)]
        elif current and len(current) + 2 + len(paragraph) > budget:
            pieces.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}" if current else paragraph
    return pieces + ([current] if current else [])


def _section(note: ParsedNote, section_id: str, heading_path: str, level: int, body: str) -> Section:
    prefix = " > ".join(filter(None, [note.title, heading_path])) + "\n\n"
    content = body.strip()
    texts = [content] if len(prefix) + len(content) <= MAX_CHARS else _pieces(body, MAX_CHARS - len(prefix))
    chunks = tuple(Chunk(id=f"{section_id}#{i}", section_id=section_id, text=prefix + t)
                   for i, t in enumerate(t for t in texts if t))
    return Section(id=section_id, heading_path=heading_path, level=level, chunks=chunks)


def chunk_note(note: ParsedNote, text: str) -> list[Section]:
    """Split a note into sections and chunks. `text` is the full note text that `note` was parsed from."""
    starts = note.heading_starts
    sections: list[Section] = []
    preamble = text[note.body_start:starts[0] if starts else len(text)]
    if preamble.strip():
        sections.append(_section(note, f"{note.path}#", "", 0, preamble))

    stack: list[tuple[int, str]] = []
    seen: dict[str, int] = {}
    for i, ((level, title), start) in enumerate(zip(note.headings, starts, strict=True)):
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        heading_path = " > ".join(t for _, t in stack)
        seen[heading_path] = seen.get(heading_path, 0) + 1
        suffix = f"~{seen[heading_path]}" if seen[heading_path] > 1 else ""
        line_end = text.find("\n", start)
        body_start = len(text) if line_end == -1 else line_end + 1
        body_end = starts[i + 1] if i + 1 < len(starts) else len(text)
        sections.append(_section(note, f"{note.path}#{heading_path}{suffix}", heading_path, level,
                                 text[body_start:body_end]))
    return sections

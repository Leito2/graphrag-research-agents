from researchcore.vault import chunk_note, parse_note
from researchcore.vault.chunker import MAX_CHARS

NL = chr(10)


def chunks_of(text: str, path: str = "Area/GraphRAG.md"):
    return chunk_note(parse_note(text, path), text)


def test_preamble_and_nested_heading_paths():
    text = NL.join(["intro line", "# Basics", "what it is", "## Local search", "seeds", "# Next", "more", ""])
    sections = chunks_of(text)
    assert [s.heading_path for s in sections] == ["", "Basics", "Basics > Local search", "Next"]
    assert [s.level for s in sections] == [0, 1, 2, 1]
    assert sections[0].id == "Area/GraphRAG.md#"
    assert sections[2].id == "Area/GraphRAG.md#Basics > Local search"
    assert sections[2].chunks[0].text == "GraphRAG > Basics > Local search" + NL + NL + "seeds"
    assert sections[0].chunks[0].text == "GraphRAG" + NL + NL + "intro line"


def test_empty_sections_have_no_chunks_and_duplicate_headings_get_unique_ids():
    text = NL.join(["# A", "## Example", "one", "## Example", "two", ""])
    sections = chunks_of(text, "n.md")
    assert sections[0].heading_path == "A" and sections[0].chunks == ()        # heading straight into another
    assert [s.id for s in sections[1:]] == ["n.md#A > Example", "n.md#A > Example~2"]
    assert [s.chunks[0].text.split(NL)[-1] for s in sections[1:]] == ["one", "two"]


def test_hash_lines_inside_code_do_not_open_sections():
    text = NL.join(["# Setup", "```bash", "# install it", "pip install x", "```", ""])
    sections = chunks_of(text)
    assert [s.heading_path for s in sections if s.level] == ["Setup"]
    assert "# install it" in sections[-1].chunks[0].text


def test_long_sections_split_on_blank_lines_then_hard_split():
    paragraph = "word " * 100                                         # 500 characters
    giant = "x" * (MAX_CHARS * 2)
    text = "# Long" + NL + (NL + NL).join([paragraph] * 5) + NL + NL + giant + NL
    chunks = chunks_of(text)[-1].chunks
    assert len(chunks) > 3
    assert all(len(c.text) <= MAX_CHARS for c in chunks)
    assert all(c.text.startswith("GraphRAG > Long" + NL + NL) for c in chunks)
    assert [c.id for c in chunks] == [f"Area/GraphRAG.md#Long#{i}" for i in range(len(chunks))]


def test_chunking_is_deterministic():
    text = NL.join(["# A", "x", "## B", "y", ""])
    assert chunks_of(text) == chunks_of(text)

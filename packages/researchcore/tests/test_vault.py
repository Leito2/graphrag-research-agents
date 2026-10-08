from researchcore.vault import LinkResolver, parse_note

NL = chr(10)

NOTE = """---
tags: [rag, graphs]
aliases: [GraphRAG intro]
---
# 🎯 Welcome — GraphRAG

See [[06 - Large Language Models/13 - vLLM and Advanced RAG/04 - GraphRAG|the GraphRAG note]] and
[[Neo4j#Cypher basics]]. Diagram: ![[graph.png]] #knowledge-graph #rag/advanced

```python
x = "[[not a link]]"  # tags in code are ignored: #nope
```
Inline `[[also not a link]]` and a heading tag:
## Section #notatag
Price is #1 in a list? No: issue #42 is not a tag either.
"""


def test_frontmatter_links_embeds_tags_headings():
    n = parse_note(NOTE, "06 - Large Language Models/35 - GraphRAG/00 - Welcome.md")
    assert n.title == "00 - Welcome"
    assert n.frontmatter["aliases"] == ["GraphRAG intro"]
    targets = {(lk.target, lk.heading, lk.alias, lk.embed) for lk in n.links}
    graphrag = "06 - Large Language Models/13 - vLLM and Advanced RAG/04 - GraphRAG"
    assert targets == {
        (graphrag, None, "the GraphRAG note", False),
        ("Neo4j", "Cypher basics", None, False),
        ("graph.png", None, None, True),
    }
    assert n.tags == {"rag", "graphs", "knowledge-graph", "rag/advanced"}
    assert n.headings == [(1, "🎯 Welcome — GraphRAG"), (2, "Section #notatag")]
    assert n.code_blocks == 1


def test_resolver_path_then_basename_case_insensitive():
    r = LinkResolver(["A/B/Neo4j.md", "A/Neo4j.md", "C/Spark Streaming.md"])
    assert r.resolve("A/B/Neo4j") == "A/B/Neo4j.md"            # exact vault path
    assert r.resolve("neo4j") == "A/Neo4j.md"                  # basename, shortest path wins
    assert r.resolve("spark streaming.md") == "C/Spark Streaming.md"
    assert r.resolve("Missing Note") is None                   # becomes a MissingNote (a gap)
    assert r.resolve_folder("a/b") == "A/B"                    # link to a course folder


def test_relative_links_and_dotted_titles():
    r = LinkResolver(["06 - LLMs/15 - MCP/00 - Welcome.md", "06 - LLMs/18 - LangGraph/LangGraph v0.2.md"])
    src = "06 - LLMs/18 - LangGraph/01 - Intro.md"
    assert r.resolve("../15 - MCP/00 - Welcome.md", source=src) == "06 - LLMs/15 - MCP/00 - Welcome.md"
    assert r.resolve("./LangGraph v0.2", source=src) == "06 - LLMs/18 - LangGraph/LangGraph v0.2.md"
    assert r.resolve("LangGraph v0.2") == "06 - LLMs/18 - LangGraph/LangGraph v0.2.md"
    assert r.resolve_folder("../15 - MCP", source=src) == "06 - LLMs/15 - MCP"
    assert r.resolve("../../../outside.md", source=src) is None          # never escapes the vault


def test_invalid_frontmatter_is_flagged_not_fatal():
    n = parse_note("---" + NL + "tags: [unclosed" + NL + "---" + NL + "# Title" + NL, "x.md")
    assert n.frontmatter_error and n.frontmatter == {} and n.headings == [(1, "Title")]

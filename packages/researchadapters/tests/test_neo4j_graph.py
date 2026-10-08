from researchadapters.neo4j_graph import constraints_cypher, is_read_only
from researchcore.graph.schema import NODE_KEYS


def test_constraints_cover_every_label():
    assert len(constraints_cypher()) == len(NODE_KEYS)
    assert all("IS UNIQUE" in c for c in constraints_cypher())


def test_text2cypher_guard():
    assert is_read_only("MATCH (n:Note)-[:LINKS_TO]->(m) RETURN n, m LIMIT 25")
    assert not is_read_only("MATCH (n:Note) DETACH DELETE n")
    assert not is_read_only("MATCH (n:Note) RETURN n")          # LIMIT is mandatory

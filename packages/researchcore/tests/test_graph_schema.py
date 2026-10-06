from researchcore.graph_schema import TRANSACTIONAL_RELS, constraints_cypher, is_read_only


def test_constraints_cover_every_label():
    assert len(constraints_cypher()) == 11
    assert all("IS UNIQUE" in c for c in constraints_cypher())


def test_transactional_rels_match_p1_contract():
    assert set(TRANSACTIONAL_RELS) == {"USES_CARD", "USES_DEVICE", "CONNECTS_FROM", "PAYS"}


def test_text2cypher_guard():
    assert is_read_only("MATCH (u:User)-[:USES_DEVICE]->(d) RETURN u, d LIMIT 25")
    assert not is_read_only("MATCH (u:User) DETACH DELETE u")
    assert not is_read_only("MATCH (u:User) RETURN u")          # LIMIT is mandatory

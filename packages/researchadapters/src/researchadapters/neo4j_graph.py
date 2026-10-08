"""Neo4j adapter (ADR-006): Cypher for the domain schema and the Text2Cypher write guard (ADR-002)."""
from researchcore.graph.schema import NODE_KEYS

WRITE_CLAUSES = ("CREATE", "MERGE", "DELETE", "DETACH", "SET", "REMOVE", "DROP", "LOAD CSV", "CALL DBMS")


def constraints_cypher() -> list[str]:
    return [
        f"CREATE CONSTRAINT {label.lower()}_{key} IF NOT EXISTS FOR (n:{label}) REQUIRE n.{key} IS UNIQUE"
        for label, key in NODE_KEYS.items()
    ]


def is_read_only(cypher: str) -> bool:
    """First guard for Text2Cypher (PLAN §4.3); the read-only DB role is the second one."""
    upper = " ".join(cypher.upper().split())
    return not any(clause in upper for clause in WRITE_CLAUSES) and " LIMIT " in f" {upper} "

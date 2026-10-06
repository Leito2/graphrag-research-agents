"""Knowledge-graph schema (PLAN §4.1). The transactional layer mirrors P1's EntityEdge contract."""
NODE_KEYS: dict[str, str] = {
    "User": "id", "Card": "id", "Device": "id", "IpCountry": "code", "Merchant": "id",
    "Document": "id", "Chunk": "id", "Entity": "id", "Typology": "id", "Community": "id", "Finding": "id",
}

# Relationship types published by P1 on topic `entity-edges` (fraudcore.contracts.EntityEdge.rel).
TRANSACTIONAL_RELS: dict[str, tuple[str, str]] = {
    "USES_CARD": ("User", "Card"),
    "USES_DEVICE": ("User", "Device"),
    "CONNECTS_FROM": ("User", "IpCountry"),
    "PAYS": ("User", "Merchant"),
}

WRITE_CLAUSES = ("CREATE", "MERGE", "DELETE", "DETACH", "SET", "REMOVE", "DROP", "LOAD CSV", "CALL DBMS")


def constraints_cypher() -> list[str]:
    return [
        f"CREATE CONSTRAINT {label.lower()}_{key} IF NOT EXISTS FOR (n:{label}) REQUIRE n.{key} IS UNIQUE"
        for label, key in NODE_KEYS.items()
    ]


def is_read_only(cypher: str) -> bool:
    """First guard for Text2Cypher (PLAN §6.4); the read-only DB role is the second one."""
    upper = " ".join(cypher.upper().split())
    return not any(clause in upper for clause in WRITE_CLAUSES) and " LIMIT " in f" {upper} "

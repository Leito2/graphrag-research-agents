// Generated from researchadapters.neo4j_graph.constraints_cypher() — applied by `make index` (M1).
CREATE CONSTRAINT note_path IF NOT EXISTS FOR (n:Note) REQUIRE n.path IS UNIQUE;
CREATE CONSTRAINT missingnote_target IF NOT EXISTS FOR (n:MissingNote) REQUIRE n.target IS UNIQUE;
CREATE CONSTRAINT folder_path IF NOT EXISTS FOR (n:Folder) REQUIRE n.path IS UNIQUE;
CREATE CONSTRAINT tag_name IF NOT EXISTS FOR (n:Tag) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (n:Concept) REQUIRE n.id IS UNIQUE;

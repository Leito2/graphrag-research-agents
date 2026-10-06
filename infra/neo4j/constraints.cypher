// Generated from researchcore.graph_schema.constraints_cypher() — applied by `make load-graph` (M1).
CREATE CONSTRAINT user_id IF NOT EXISTS FOR (n:User) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT card_id IF NOT EXISTS FOR (n:Card) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT device_id IF NOT EXISTS FOR (n:Device) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT ipcountry_code IF NOT EXISTS FOR (n:IpCountry) REQUIRE n.code IS UNIQUE;
CREATE CONSTRAINT merchant_id IF NOT EXISTS FOR (n:Merchant) REQUIRE n.id IS UNIQUE;

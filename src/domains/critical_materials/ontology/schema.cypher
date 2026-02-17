// Critical materials ontology scaffold
CREATE CONSTRAINT material_name IF NOT EXISTS
FOR (m:Material) REQUIRE m.name IS UNIQUE;

CREATE CONSTRAINT country_name IF NOT EXISTS
FOR (c:Country) REQUIRE c.name IS UNIQUE;

CREATE CONSTRAINT company_name IF NOT EXISTS
FOR (c:Company) REQUIRE c.name IS UNIQUE;

// Example relationship patterns:
// (:Material)-[:EXTRACTED_IN]->(:Country)
// (:Material)-[:PROCESSED_IN]->(:Country)
// (:Company)-[:OPERATES]->(:Mine)
// (:Country)-[:EXPORTS_TO]->(:Country)
// (:Material)-[:SUBSTITUTED_BY]->(:Material)


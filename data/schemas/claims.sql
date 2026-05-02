-- atlasmind_claims.claims — every claim ever produced by any agent.

CREATE TABLE IF NOT EXISTS `${PROJECT}.atlasmind_claims.claims` (
  run_id        STRING NOT NULL,
  agent         STRING NOT NULL,
  as_of         TIMESTAMP NOT NULL,
  statement     STRING NOT NULL,
  confidence    STRING NOT NULL,        -- low | medium | high
  evidence      ARRAY<STRUCT<
                  source STRING,
                  url STRING,
                  as_of TIMESTAMP,
                  excerpt STRING
                >> NOT NULL,
  early_warning ARRAY<STRING>,
  tags          ARRAY<STRING>,
  country_iso3  STRING,
  sector        STRING,
  loaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(as_of)
CLUSTER BY run_id, agent;

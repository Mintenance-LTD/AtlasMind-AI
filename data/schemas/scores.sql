-- atlasmind_scores.scores — score history; supports replay under revised weights.

CREATE TABLE IF NOT EXISTS `${PROJECT}.atlasmind_scores.scores` (
  run_id        STRING NOT NULL,
  agent         STRING NOT NULL,
  country_iso3  STRING,
  sector        STRING,
  score_name    STRING NOT NULL,        -- political_risk, market_opportunity, etc.
  score_value   FLOAT64 NOT NULL,
  score_version STRING,                  -- e.g. "v1.0"
  inputs        JSON,                    -- raw inputs for replayability
  weights       JSON,                    -- weights used
  as_of         TIMESTAMP NOT NULL
)
PARTITION BY DATE(as_of)
CLUSTER BY country_iso3, score_name;

-- atlasmind_runs.runs — one row per strategic question.

CREATE TABLE IF NOT EXISTS `${PROJECT}.atlasmind_runs.runs` (
  run_id          STRING NOT NULL,
  requested_by    STRING NOT NULL,
  scope_country   STRING,
  scope_region    STRING,
  scope_sector    STRING,
  scope_theme     STRING,
  horizon_months  INT64,
  depth           STRING,
  started_at      TIMESTAMP NOT NULL,
  finished_at     TIMESTAMP,
  status          STRING,         -- pending | running | succeeded | failed
  agent_count     INT64,
  total_tokens    INT64,
  cost_usd_estimate FLOAT64
)
PARTITION BY DATE(started_at)
CLUSTER BY run_id;

CREATE TABLE IF NOT EXISTS `${PROJECT}.atlasmind_runs.ingest_runs` (
  ingest_id   STRING NOT NULL,
  source      STRING NOT NULL,
  as_of       TIMESTAMP NOT NULL,
  rows_in     INT64,
  rows_loaded INT64,
  checksum    STRING,
  gcs_uri     STRING,
  status      STRING
)
PARTITION BY DATE(as_of)
CLUSTER BY source;

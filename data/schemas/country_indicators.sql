-- atlasmind_warehouse.country_indicators
-- One row per (country, indicator, as_of). Long format for easy joins.

CREATE TABLE IF NOT EXISTS `${PROJECT}.atlasmind_warehouse.country_indicators` (
  country_iso3   STRING NOT NULL,
  indicator      STRING NOT NULL,
  value          FLOAT64,
  unit           STRING,
  as_of          DATE NOT NULL,
  source         STRING NOT NULL,
  source_dataset STRING,
  ingest_id      STRING,
  loaded_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY as_of
CLUSTER BY country_iso3, indicator;

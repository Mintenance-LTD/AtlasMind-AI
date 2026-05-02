# Fixtures

Canned data so AtlasMind agents and tests run with no GCP credentials.
The fixture backend is selected by `ATLASMIND_BQ_BACKEND=fixture` (which is
the default until the GCP projects in `docs/GCP_SETUP.md` are provisioned).

Each fixture is a snapshot pulled from a public source on a known date,
checked in deliberately so behaviour is deterministic. The `as_of_year`
field tells the agent how stale the data is; agents must surface that in
claim citations.

## Layout

```
data/fixtures/
└── bigquery/
    └── wdi/
        ├── COG.json    Republic of Congo
        ├── NGA.json    Nigeria
        ├── KEN.json    Kenya
        └── ...
```

Each `<ISO3>.json` is a flat map of `WDI indicator code -> {value, year, source}`.

To swap to live data: `export ATLASMIND_BQ_BACKEND=live`.

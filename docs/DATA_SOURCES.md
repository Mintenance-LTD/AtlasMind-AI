# AtlasMind AI — Data Sources

Every agent's claim must cite at least one source. This catalogue is the master list of feeds AtlasMind ingests and queries. All data lands in `gs://atlasmind-raw/` first and is normalised into `atlasmind_warehouse`.

---

## Tiers

- **Tier 0 — Free, in BigQuery already.** Use the BigQuery public datasets program. No ingestion required.
- **Tier 1 — Free public APIs.** Pulled by Cloud Functions/Cloud Run jobs on a schedule.
- **Tier 2 — Free with terms.** Requires registration, attribution, or non-commercial-only.
- **Tier 3 — Paid / licensed.** Held back to v2 unless a licence exists.

---

## Geopolitics

| Source | Tier | Notes |
|---|---|---|
| World Bank Worldwide Governance Indicators (WGI) | T0 | `bigquery-public-data.world_bank_wdi` adjacent |
| Freedom House — Freedom in the World | T1 | CSV, annual |
| Transparency International — CPI | T1 | CSV, annual |
| ACLED — armed conflict events | T2 | Free for non-commercial; commercial licence needed |
| UCDP — conflict dataset | T1 | Free |
| GDELT 2.0 — global news events | T0 | Available as BigQuery public dataset |
| National election calendars (IFES + IDEA) | T1 | Combined into `atlasmind_warehouse.elections` |
| OFAC / EU / UK sanctions lists | T1 | Daily refresh |
| IMF Article IV consultations | T2 | Indexed into Vertex AI Search |
| Central bank monetary-policy statements | T1 | Per-country fetcher |

---

## Markets & macro

| Source | Tier | Notes |
|---|---|---|
| World Bank WDI | T0 | `bigquery-public-data.world_bank_wdi` |
| IMF WEO | T1 | API + bulk download |
| OECD MEI | T1 | API |
| BIS — credit, FX | T1 | CSV |
| Yahoo Finance / Stooq — equities, FX (free tier) | T1 | For indices and majors |
| Google Finance via grounding | T0 | For live quote context only |
| FRED (St Louis Fed) | T1 | Macro series |
| London Metal Exchange / EIA — commodities | T1 | EIA free; LME via licensed feed |

> v1 uses end-of-day data only. Real-time tickers are out of scope.

---

## Population & demographics

| Source | Tier | Notes |
|---|---|---|
| UN World Population Prospects (WPP) | T1 | Tables & API |
| UN World Urbanization Prospects | T1 | Tables |
| World Bank — Health, education, jobs | T0 | WDI |
| WorldPop | T2 | High-res grids; via Earth Engine |
| GHS (Global Human Settlement) | T2 | Via Earth Engine |
| National statistics offices (per country) | T1 | Country-by-country fetchers |
| ILO — labour statistics | T1 | API |
| UNESCO — education | T1 | API |

---

## Geospatial / Earth Engine

| Source | Tier | Notes |
|---|---|---|
| Sentinel-2 imagery | T0 | Earth Engine |
| Landsat 8/9 | T0 | Earth Engine |
| VIIRS night-lights | T0 | Earth Engine — proxy for economic activity |
| WorldPop population grids | T0 (EE) | Density and change |
| ESA WorldCover | T0 | Land cover |
| MODIS NDVI | T0 | Agriculture/drought signals |

Earth Engine results are exported to BigQuery as country/admin-level indicators on a monthly schedule.

---

## Technology trends

| Source | Tier | Notes |
|---|---|---|
| Google Trends | T0 | Public BigQuery dataset |
| YouTube Data API | T1 | Quota-limited |
| GitHub Archive | T0 | `bigquery-public-data.githubarchive` |
| Stack Overflow | T0 | Public BigQuery |
| USPTO + EPO patents | T0 | Public BigQuery |
| Crunchbase (free fields only) | T2 | Or via Workspace partner |
| Product Hunt | T1 | Indexed into Vertex AI Search |
| App Store / Play category snapshots | T1 | Daily scrape, normalised by region |

---

## Country & investment context

| Source | Tier | Notes |
|---|---|---|
| Government budget / capex announcements | T1 | Per-country PDF ingestion → Vertex AI Search |
| Sovereign wealth fund disclosures | T1 | Public reports |
| Multilateral lending pipelines (World Bank, AfDB, AIIB) | T1 | Project pipelines |
| Doing Business legacy + B-Ready (when published) | T1 | World Bank |
| FDI Markets (greenfield) | T3 | Paid; deferred |

---

## Refresh schedule (v1)

| Cadence | Sources |
|---|---|
| Hourly | Sanctions deltas, central-bank releases (RSS) |
| Daily | FX, equities EOD, commodity prices, GDELT, news index |
| Weekly | App store rankings, YouTube category snapshots, Trends |
| Monthly | Earth Engine indicator exports, IMF/OECD updates |
| Quarterly | UN WPP refresh check, sovereign disclosures |
| Annual | WGI, CPI, Freedom House |

All schedules live in `infra/terraform/scheduler.tf`.

---

## Ingestion contract

Every loader produces a row in `atlasmind_warehouse.ingest_runs`:

```
ingest_id     STRING   -- uuid
source        STRING   -- e.g. "worldbank_wdi"
as_of         TIMESTAMP
rows_in       INT64
rows_loaded   INT64
checksum      STRING
gcs_uri       STRING
status        STRING   -- ok | partial | failed
```

This makes provenance auditable: any agent claim can be traced to the exact ingest run that produced its source data.

---

## Licensing & attribution

The Strategy Briefing Agent footnote on every Doc and Slide deck includes:

> *Sources: <comma-separated source list with as-of dates>. AtlasMind AI does not redistribute licensed third-party data; it presents derived analysis with citations.*

A licence-aware filter in `core/tools/citations.py` strips claims whose only evidence comes from a source whose licence forbids the current user's intended use.

# AtlasMind AI — Architecture

This document describes how the eight agents, the data plane, and the user-facing surfaces fit together. Read [`TECH_PACK.md`](TECH_PACK.md) first for the high-level decisions.

---

## 1. Logical layers

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Surface layer                                            │
│    Next.js dashboard · Looker Studio · Drive (Docs/Slides)  │
├─────────────────────────────────────────────────────────────┤
│ 2. API layer                                                │
│    atlasmind-api (Cloud Run)  ·  IAP + Workspace SSO        │
├─────────────────────────────────────────────────────────────┤
│ 3. Orchestration layer                                      │
│    Strategy Conductor (Vertex AI Agent Builder + ADK)       │
├─────────────────────────────────────────────────────────────┤
│ 4. Agent layer                                              │
│    8 Cloud Run services, each its own Gemini-powered agent  │
├─────────────────────────────────────────────────────────────┤
│ 5. Tool layer                                               │
│    BigQuery, Earth Engine, Maps, Trends, Search grounding,  │
│    Vertex AI Search, Drive/Docs/Slides, Sheets              │
├─────────────────────────────────────────────────────────────┤
│ 6. Data layer                                               │
│    BigQuery warehouse + Cloud Storage raw zone              │
├─────────────────────────────────────────────────────────────┤
│ 7. Ingestion layer                                          │
│    Cloud Scheduler → Cloud Functions / Cloud Run jobs       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Run lifecycle

A *run* is one strategic question (e.g. "Brief me on Republic of Congo, 24-month horizon"). Every run is identified by a `run_id` and is fully replayable.

```
[1] User submits question on dashboard
        │
        ▼
[2] atlasmind-api validates, persists Run row in Firestore,
    publishes RunRequested to Pub/Sub
        │
        ▼
[3] Strategy Conductor receives RunRequested
        │
        ▼
[4] Conductor builds an execution plan:
       parallel:  Geopolitical, Market, Population, Tech Trend
       then:      Country Risk  (depends on Geopol + Market + Popln)
       then:      Investment    (depends on all of the above)
       then:      Scenario      (uses everything)
       finally:   Strategy Briefing
        │
        ▼
[5] Each agent:
       reads context from Agent Memory (Firestore + BigQuery)
       calls its tools (BigQuery, Earth Engine, Search, etc.)
       writes claims + scores back to Agent Memory
       publishes AgentCompleted event
        │
        ▼
[6] Strategy Briefing Agent reads all claims,
    composes Doc + Slides via Workspace APIs,
    drops them in the user's Drive folder
        │
        ▼
[7] atlasmind-api notifies user (email + in-app)
```

Pub/Sub topics:
- `runs.requested`
- `agents.completed`
- `runs.completed`
- `alerts.triggered`

---

## 3. Agent execution model

Each agent is:

- A **Cloud Run service** (one container per agent) under `atlasmind-prod`.
- Built from `agents/<name>/` using a shared `core/` library.
- Triggered either by Pub/Sub push (`agents.completed`) or by direct invocation from the Strategy Conductor.
- Stateless across requests — all state goes through Agent Memory.
- Wrapped in a **Vertex AI Agent Builder** definition that exposes its capabilities to the Conductor via ADK's agent-to-agent protocol.

Inside an agent:

```
HTTP request
   │
   ▼
core.runtime.AgentRunner
   │
   ├── load context     → Firestore + BigQuery
   ├── plan             → Gemini 2.5 Pro
   ├── execute tools    → BigQuery / Search / Earth Engine / etc.
   ├── compose claims   → with citations + confidence
   ├── score            → core.scoring
   └── persist          → BigQuery (claims) + Firestore (run state)
   │
   ▼
HTTP response (AgentResult)
```

---

## 4. Agent Memory

Two stores, one logical interface (`core.memory.AgentMemory`):

| Store | Holds | Why |
|---|---|---|
| **Firestore** (`atlasmind-prod`) | Live run state, conductor checkpoints, user workspaces, watchlists | Low-latency document reads/writes |
| **BigQuery** (`atlasmind_warehouse`) | All emitted claims, scores, evidence, run logs | Analytical replay, scoring history, eval |

Every claim ever produced is persisted to BigQuery `claims` table with `run_id`, `agent`, `as_of`, `confidence`, `evidence_urls[]`, so any briefing can be reconstructed.

---

## 5. Data flow into the warehouse

```
Cloud Scheduler ──► Cloud Function / Cloud Run job
                          │
                          ├── BigQuery public datasets  (World Bank, IMF, Census)
                          │       └── scheduled MERGE into atlasmind_warehouse.*
                          │
                          ├── External APIs (UN, ACLED, OECD, FX, equities)
                          │       └── land in gs://atlasmind-raw/<source>/<date>/
                          │       └── BigQuery external table or batch load
                          │
                          ├── Earth Engine                 (image collections)
                          │       └── exported indicators to BigQuery
                          │
                          └── Google Trends / YouTube / Play
                                  └── Trends API → BigQuery
```

All raw payloads land in `gs://atlasmind-raw/` first, then are normalised into `atlasmind_warehouse`. No agent ever queries an external API in the hot path — they query BigQuery or Vertex AI Search.

The only exception is the **Geopolitical Agent**, which uses live Google Search grounding for breaking-news context.

---

## 6. Grounding & retrieval

Two retrieval modes, used together:

1. **Vertex AI Search** index (`atlasmind-knowledge`)
   - Sources: policy docs, IMF Article IV reports, central bank releases, company filings, country strategy papers.
   - Refreshed nightly.
   - Used by all reasoning-heavy agents.

2. **Google Search grounding** (built-in Gemini tool)
   - Used for current events.
   - Always returns citations; no claim is allowed without a source link.

---

## 7. Surfacing outputs

| Output | Surface | Tech |
|---|---|---|
| Country dashboard | Web app | Next.js → Cloud Run → BigQuery |
| Score heat maps | Looker Studio | Native BigQuery connector |
| Opportunity map | Web app overlay | Maps Platform + BigQuery GIS |
| Executive brief (1 page) | Drive | Docs API from template |
| Board deck | Drive | Slides API from template |
| Scorecard | Drive | Sheets API |
| Alerts | Email + in-app | Pub/Sub → Cloud Function → Workspace email |

All artefacts are owned by the user's Workspace organisation, not by AtlasMind. The platform writes to Drive on the user's behalf via OAuth (domain-wide delegation for Workspace customers; per-user OAuth for individual accounts).

---

## 8. Environments

| Env | Project | Purpose |
|---|---|---|
| dev | engineer's own GCP project | Local-loop development |
| stage | `atlasmind-stage` | Pre-prod, integration tests, eval suite |
| prod | `atlasmind-prod` | Live |

Promotion: Cloud Build pipeline → Artifact Registry → Cloud Run revision tagged with git SHA. Manual promotion gate from stage to prod.

---

## 9. Observability

- **Cloud Logging** — structured logs with `run_id`, `agent`, `tool`, `latency_ms`.
- **Cloud Trace** — every run produces one trace with one span per agent + per tool call.
- **Vertex AI Eval** — nightly eval suite scores each agent against a golden set in `eval/`.
- **Looker Studio (internal)** — agent latency, token cost per run, claim-citation rate, score drift.

---

## 10. Why this shape

- **Agent isolation** — one Cloud Run service per agent means we can ship, scale, and debug agents independently.
- **Replayability** — claims-as-data in BigQuery means any briefing can be regenerated, audited, or re-scored under new weights.
- **Single-vendor security** — Workspace SSO + IAM + VPC-SC gives one perimeter and one identity story.
- **Workspace-native outputs** — briefings live in Drive as Docs/Slides, not as PDFs in an opaque app, which matches how strategic users actually work.

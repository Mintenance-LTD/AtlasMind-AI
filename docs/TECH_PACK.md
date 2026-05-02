# AtlasMind AI — Tech Pack

This is the complete technical specification for AtlasMind AI, a strategic intelligence platform built entirely on Google Workspace + Google Cloud.

---

## 1. Product principle

AtlasMind AI is a **decision-support system**. Every output answers the question:

> *"Given the current evidence, what should a strategic decision-maker pay attention to, and how confident can they be?"*

The system never produces unhedged predictions. Outputs always include:

- A claim
- The evidence
- A confidence band (Low / Medium / High)
- The early-warning indicators that would change the picture

---

## 2. Users and use cases

### Primary users
- **Investors** evaluating country, sector, or theme exposure
- **Policymakers** assessing national strategy and risk
- **Operators** (e.g. Mintenance) deciding where to deploy infrastructure or products
- **Analysts** producing structured intelligence briefings

### v1 anchor use case
> *Country & market opportunity intelligence dashboard.*

A user picks a country (e.g. Republic of Congo), and the platform returns:

- Strategic position summary
- Growth drivers and risks
- Population trend
- Top investment opportunities (scored)
- Warning signals
- Downloadable 1-page board brief (Google Docs) and deck (Google Slides)

All eight agents contribute to that output.

---

## 3. The eight agents

Full specs live in [`AGENTS.md`](AGENTS.md). Summary:

| # | Agent | Inputs | Outputs |
|---|---|---|---|
| 1 | Geopolitical | News, policy docs, election calendars, conflict feeds | Political risk score + drivers |
| 2 | Market | Equities, FX, commodities, rates, macro | Sector signals + macro regime read |
| 3 | Investment | Outputs of #1, #2, #4, #6 | Ranked opportunity list with rationale |
| 4 | Population | UN, World Bank, national stats | Demographic trend + labour-market read |
| 5 | Technology Trend | App stores, Trends, YouTube, Product Hunt, GitHub, patents | Emerging-trend dossier |
| 6 | Country Risk | Outputs of #1, #2, #4 + governance indicators | Country risk scorecard (0–100) |
| 7 | Scenario | Outputs of #1–#6 | 3 named futures + probabilities + indicators |
| 8 | Strategy Briefing | Outputs of #1–#7 | Board-grade Doc + Slides |

Agents are independent services. They communicate through Pub/Sub and a shared **Agent Memory** store (Firestore + BigQuery), and are orchestrated by the **Strategy Conductor** in `core/orchestrator/`.

---

## 4. System architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                       USER (Workspace SSO)                         │
│              Next.js dashboard on Firebase Hosting                 │
└───────────────┬────────────────────────────────┬───────────────────┘
                │                                │
        Firebase Auth                  Looker Studio dashboards
                │                                │
                ▼                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                       API GATEWAY (Cloud Run)                      │
│           atlasmind-api · IAP-protected · Workspace SSO            │
└───────────────┬────────────────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────────────┐
│                  STRATEGY CONDUCTOR (Cloud Run)                    │
│      Vertex AI Agent Builder · Multi-agent orchestration (ADK)     │
└───┬────────┬────────┬────────┬────────┬────────┬────────┬─────────┘
    │        │        │        │        │        │        │
    ▼        ▼        ▼        ▼        ▼        ▼        ▼
 Geopol   Market  Invest   Popln   TechTrd  CtryRsk  Scenario
 Agent    Agent   Agent    Agent   Agent    Agent    Agent
   │        │       │        │       │        │        │
   └────────┴───────┴────────┴───────┴────────┴────────┘
                              │
                              ▼
                  Strategy Briefing Agent
                              │
                              ▼
              Docs / Slides / Sheets API → Drive
                              │
                              ▼
                     User receives briefing
```

### Data plane

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Public data  │    │ Live signals │    │ User uploads │
│ (BQ public,  │    │ (news, APIs) │    │ (Drive)      │
│  Earth Eng.) │    │              │    │              │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └─────────┬─────────┴─────────┬─────────┘
                 ▼                   ▼
        ┌─────────────────┐  ┌────────────────┐
        │   BigQuery      │  │ Cloud Storage  │
        │ atlasmind_warehs│  │ atlasmind-raw  │
        └────────┬────────┘  └────────┬───────┘
                 │                    │
                 └─────────┬──────────┘
                           ▼
                ┌─────────────────────┐
                │  Vertex AI Search   │
                │ (grounding index)   │
                └─────────────────────┘
```

---

## 5. GCP project layout

One Google Workspace organisation, four GCP projects:

| Project ID (suggested) | Purpose |
|---|---|
| `atlasmind-prod` | Production agents, BigQuery warehouse, Firebase, Cloud Run |
| `atlasmind-stage` | Staging mirror — same shape, smaller scale |
| `atlasmind-data` | Raw ingestion, BigQuery scratch, Earth Engine assets |
| `atlasmind-shared` | Artifact Registry, Cloud Build, Secret Manager, logs sink |

Folder structure in the Workspace org:

```
atlasmind.ai (Workspace org)
└── AtlasMind/
    ├── Production/      → atlasmind-prod
    ├── Staging/         → atlasmind-stage
    ├── Data/            → atlasmind-data
    └── Shared/          → atlasmind-shared
```

VPC Service Controls perimeter wraps `atlasmind-prod` + `atlasmind-data`.

---

## 6. Core technology choices

| Concern | Choice | Why |
|---|---|---|
| Agent runtime | **Python 3.12 + Vertex AI ADK** | First-class Gemini support, agent-to-agent protocol, tool-use |
| Orchestration | Vertex AI Agent Builder | Hosted multi-agent runtime with eval + tracing |
| LLM | **Gemini 2.5 Pro** for reasoning, **Gemini 2.5 Flash** for high-volume signal classification | Best price/quality on Google |
| Grounding | **Vertex AI Search** + Google Search grounding | Fresh, citable answers |
| Warehouse | **BigQuery** (multi-region `EU` for v1) | Native joins with World Bank, IMF, Census public datasets |
| Vector store | **BigQuery vector search** + **Vertex AI Vector Search** for hot paths | Avoid extra infra |
| Geospatial | **Earth Engine** (Python API) + **Maps Platform** | Satellite signals (urban growth, lights, agriculture) |
| Backend services | **Cloud Run** (containerised, autoscale-to-zero) | Each agent = one Cloud Run service |
| Async / fanout | **Pub/Sub** + **Cloud Scheduler** | Scheduled scans + event-driven agent runs |
| Frontend | **Next.js 15** on **Firebase Hosting** + Firebase Auth | Workspace SSO out of the box |
| User data | **Firestore** | Workspaces, saved briefings, watchlists |
| Output artefacts | **Google Docs / Slides / Sheets API** + Drive | Briefings are native Workspace docs |
| Dashboards | **Looker Studio** Pro | Country profiles, opportunity heat maps |
| CI/CD | **Cloud Build** + Artifact Registry | Native to GCP |
| IaC | **Terraform** (Google provider) | Reproducible projects |
| Secrets | **Secret Manager** | API keys for non-Google sources |
| Observability | **Cloud Logging**, **Cloud Trace**, **Vertex AI Eval** | Built-in |

---

## 7. Agent contract

Every agent — without exception — follows the same contract.

### Input
```json
{
  "run_id": "uuid",
  "scope": {
    "country": "COG",
    "sector": "infrastructure",
    "horizon_months": 24
  },
  "depth": "standard | deep",
  "requested_by": "user@workspace"
}
```

### Output
```json
{
  "run_id": "uuid",
  "agent": "geopolitical",
  "as_of": "2026-05-02T00:00:00Z",
  "claims": [
    {
      "statement": "...",
      "confidence": "low | medium | high",
      "evidence": [{"source": "...", "url": "...", "as_of": "..."}],
      "early_warning": ["..."]
    }
  ],
  "scores": {"political_risk": 62},
  "raw_signals_uri": "gs://atlasmind-raw/runs/<run_id>/geopolitical.jsonl"
}
```

This is enforced by Pydantic models in `core/schemas/`.

---

## 8. Scoring framework

AtlasMind exposes seven scores per country/sector. Each is a 0–100 composite with documented weights (see [`AGENTS.md` §scoring](AGENTS.md)):

1. Political Risk Score
2. Market Opportunity Score
3. Demographic Growth Score
4. Infrastructure Gap Score
5. Technology Adoption Score
6. Investment Readiness Score
7. Strategic Importance Score

Each score is reproducible: the inputs, weights, and as-of date are stored in BigQuery so any score can be replayed.

---

## 9. Outputs

The Strategy Briefing Agent produces, per run:

- **1-page executive brief** — Google Doc, generated via Docs API from a template
- **Board pack** — Google Slides deck with country profile, scores, opportunities, scenarios
- **Investment scorecard** — Google Sheet with sortable opportunities
- **Risk heat map** — Looker Studio link
- **Opportunity map** — Maps Platform tile layer
- **Alert subscription** — Pub/Sub-driven email when any score moves > threshold

All artefacts are saved to a **Workspace shared drive** owned by the user's organisation.

---

## 10. Security & responsible-use posture

See [`SECURITY.md`](SECURITY.md). Key points:

- All access via Workspace SSO + IAM; no service accounts with keys checked in.
- VPC Service Controls perimeter prevents data exfiltration from the warehouse.
- Every agent output is **citation-bound** — the UI shows the source on hover.
- The Strategy Briefing Agent is forbidden by system prompt from issuing unhedged predictions or financial advice.
- Sensitive country data is tagged and access-controlled per Workspace group.

---

## 11. Cost shape (rough order-of-magnitude, EU multi-region)

| Component | Driver | Indicative monthly cost (light usage) |
|---|---|---|
| Gemini 2.5 Pro/Flash | Tokens | $200–$2,000 |
| BigQuery storage + queries | TB scanned | $50–$500 |
| Cloud Run (8 services) | Request-seconds | $50–$300 |
| Vertex AI Search | QPS + index size | $100–$500 |
| Earth Engine | Free tier for non-commercial; Pro tier for commercial | $0–$$$ |
| Maps Platform | Requests | $0–$200 |
| Firebase + Firestore | DAU + reads | $0–$100 |
| Looker Studio Pro | Per user | $9/user/mo |

These are guides only. The Terraform stack tags every resource with `cost_center=atlasmind` so billing exports answer this precisely.

---

## 12. Out of scope for v1

To keep v1 shippable, the following are deferred:

- Real-time market data with sub-minute latency (use end-of-day for v1)
- Proprietary news licensing (use Google Search grounding + open feeds for v1)
- Mobile app (web-only)
- Custom alternative-data feeds (satellite signals limited to Earth Engine)
- On-prem or non-Google deployment

---

## 13. Definition of "done" for v1

- A Workspace user can sign in, pick a country, and within ~3 minutes receive a Doc + Slides briefing in their Drive.
- All eight agents have produced at least one citation-bound claim.
- Looker Studio dashboard renders the seven scores for that country.
- Cloud Logging shows traces for the full run.
- The same run can be replayed from BigQuery.

See [`ROADMAP.md`](ROADMAP.md) for the path to that milestone.

# AtlasMind AI

**Strategic Intelligence Operating System** — an eight-agent platform that helps decision-makers think strategically across geopolitics, markets, investment, demographics, and technology trends.

AtlasMind AI is a decision-support system, not a prediction machine. It collects signals, compares scenarios, scores risk, and produces board-grade briefings so humans can make better strategic decisions.

> Status: **scaffolding / pre-alpha**. Repo contains the architecture, tech pack, and module stubs. See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the build plan.

---

## The eight agents

| # | Agent | Purpose |
|---|---|---|
| 1 | **Geopolitical Agent** | Political risk, conflict, alliances, sanctions, elections |
| 2 | **Market Agent** | Stocks, commodities, currencies, interest rates, macro |
| 3 | **Investment Agent** | Scores opportunities by risk, return, timing, strategic fit |
| 4 | **Population Agent** | Demographics, migration, urbanisation, labour force |
| 5 | **Technology Trend Agent** | Apps, AI, software, consumer attention, patents |
| 6 | **Country Risk Agent** | Nation-by-nation investment & stability scores |
| 7 | **Scenario Agent** | "What-if" futures and stress scenarios |
| 8 | **Strategy Briefing Agent** | Synthesises everything into board-style reports |

## Google-only stack

Every layer runs on Google Workspace + Google Cloud — one identity system, one bill, one security perimeter.

| Layer | Google product |
|---|---|
| Reasoning | Gemini 2.5 Pro / Flash on **Vertex AI** |
| Agent framework | **Vertex AI Agent Builder** + **Agent Development Kit (ADK)** |
| Grounding | Google Search grounding + **Vertex AI Search** |
| Data warehouse | **BigQuery** + BigQuery public datasets (World Bank, IMF, Census, Trends) |
| Geospatial | **Google Earth Engine** + **Maps Platform** |
| Trends signals | **Google Trends**, **YouTube Data API**, Play Console signals |
| Outputs | **Docs / Slides / Sheets API**, Cloud Storage, Drive |
| Frontend | **Firebase** Hosting + Auth + Firestore (Next.js app) |
| Backend runtime | **Cloud Run**, **Cloud Functions**, **Pub/Sub**, **Cloud Scheduler** |
| Analyst workspace | **Colab Enterprise**, **Looker Studio** |
| Security | **IAM**, **Secret Manager**, **VPC Service Controls** |

## Repository layout

```
AtlasMind-AI/
├── docs/                # Architecture, tech pack, agent specs, data sources, GCP setup
├── core/                # Shared agent infra: orchestrator, memory, tools, scoring
├── agents/              # The 8 agents
│   ├── geopolitical/
│   ├── market/
│   ├── investment/
│   ├── population/
│   ├── technology_trend/
│   ├── country_risk/
│   ├── scenario/
│   └── strategy_briefing/
├── data/                # BigQuery loaders + schemas
├── functions/           # Cloud Functions (event handlers, alerts)
├── frontend/            # Next.js + Firebase web app
├── infra/               # Terraform for GCP
├── notebooks/           # Colab Enterprise notebooks
└── pyproject.toml
```

## Start here

1. Read [`docs/TECH_PACK.md`](docs/TECH_PACK.md) — full system specification.
2. Read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how the agents and data flow fit together.
3. Read [`docs/AGENTS.md`](docs/AGENTS.md) — what each agent does, its inputs, outputs, and tools.
4. Read [`docs/GCP_SETUP.md`](docs/GCP_SETUP.md) — Workspace + GCP project setup.
5. Read [`docs/ROADMAP.md`](docs/ROADMAP.md) — phased build plan.

## Important framing

AtlasMind AI never says "this stock will rise" or "this country will collapse." Every output is framed as:

> *Based on available evidence, these are the most likely scenarios, confidence levels, risks, and early-warning indicators.*

That framing is enforced in the agent prompts and the briefing schema.

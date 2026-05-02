# AtlasMind AI — Roadmap

A phased build plan to get from the empty repo you're reading now to a production-grade strategic intelligence platform. Each phase ends in a demonstrable milestone.

---

## Phase 0 — Repo & docs (this commit)

**Done when**: scaffolding, tech pack, agent specs, GCP setup, security posture, and skeleton modules exist on `claude/strategic-intelligence-platform-7uPWg`.

✅ Architecture written
✅ Eight agents specified
✅ Repo skeleton committed
✅ Terraform skeleton in place

---

## Phase 1 — GCP foundation

**Goal**: stand up the four projects, IAM, and the data warehouse.

- Provision `atlasmind-prod / stage / data / shared` via Terraform.
- Enable APIs.
- Create BigQuery datasets, Cloud Storage buckets, Artifact Registry, Secret Manager.
- Set up VPC + VPC-SC perimeter (skeleton policy in stage first).
- Cloud Build pipelines green for the agent base image.

**Demo**: `terraform apply` cleanly creates everything, and `gcloud builds submit` produces a tagged base image.

---

## Phase 2 — Data plane

**Goal**: real data flowing into BigQuery.

- Wire BigQuery public datasets (World Bank, IMF, Census, Trends, GitHub Archive).
- Build ingestion jobs for: WGI, CPI, Freedom House, ACLED (free tier), UN WPP, GDELT.
- Earth Engine monthly export job for VIIRS night-lights and WorldPop indicators.
- `ingest_runs` table populated; data lineage queryable.
- Vertex AI Search datastore `atlasmind-knowledge` indexed.

**Demo**: open BigQuery and run a SQL query that returns governance + macro + demographic data for any country.

---

## Phase 3 — Core agent infrastructure

**Goal**: shared library that every agent uses.

- `core/runtime/` — agent runner, retries, tracing
- `core/memory/` — Firestore + BigQuery memory
- `core/tools/` — BigQuery tool, Search tool, Earth Engine tool, Maps tool, Citations validator
- `core/scoring/` — score formulas, weights versioning
- `core/schemas/` — Pydantic models for input/output contracts

**Demo**: a unit test runs a fake agent end-to-end with mocked tools and produces a contract-valid output.

---

## Phase 4 — First two agents (Country Risk + Population)

**Goal**: prove the pattern with the most data-driven agents first.

- Population Agent: uses BigQuery + Earth Engine, returns demographic scores and claims.
- Country Risk Agent: composes scores from Population + governance reference data.
- Both deployed to Cloud Run in `atlasmind-stage`.
- One Vertex AI Agent Builder agent per service.

**Demo**: hit the Country Risk endpoint with `country=COG` and get a citation-bound JSON response.

---

## Phase 5 — Remaining six agents

In order:
1. Geopolitical Agent
2. Market Agent
3. Technology Trend Agent
4. Investment Agent
5. Scenario Agent
6. Strategy Briefing Agent

Each agent ships with an eval golden set and a CI gate.

**Demo**: full eight-agent run for a country produces all claims and scores in BigQuery.

---

## Phase 6 — Strategy Conductor

**Goal**: orchestration tying it all together.

- Vertex AI Agent Builder multi-agent app.
- Pub/Sub-driven fanout / dependency resolution.
- Run-state machine in Firestore.
- Cloud Trace shows the whole run as one trace.

**Demo**: one API call kicks off all eight agents in the correct order.

---

## Phase 7 — Outputs & Workspace integration

**Goal**: briefings show up in Drive.

- Doc, Slides, Sheets templates loaded into `gs://atlasmind-templates`.
- Briefing Agent fills templates via Workspace APIs.
- Domain-wide delegation set up for internal Workspace.
- External-client OAuth flow built.
- Looker Studio dashboards built and embedded.

**Demo**: a Workspace user clicks "Generate brief" and within ~3 minutes their Drive contains a Doc + Slides + Sheet.

---

## Phase 8 — Frontend

**Goal**: the dashboard.

- Next.js 15 app on Firebase Hosting.
- Pages: Country, Sector, Trend, Watchlist, Run history, Briefing viewer.
- Looker Studio embedded panels.
- Maps Platform overlay for opportunity map.
- Email + in-app alerts.

**Demo**: end users sign in, browse countries, run briefings, and view results.

---

## Phase 9 — Eval, observability, hardening

- Vertex AI Eval golden suites for all eight agents wired into CI.
- Cloud Trace dashboards for latency and cost per run.
- Looker Studio "AtlasMind Internal" dashboard for token spend, failure rate, score drift.
- Pen-test of API gateway and OAuth flow.
- VPC-SC perimeter promoted from dry-run to enforced.

---

## Phase 10 — Pilot

- Onboard 2–3 internal users (Mintenance team, an investor friendly, a policymaker).
- Run real country briefings; capture feedback.
- Fix top-10 issues; tag `v1.0.0`.

---

## Beyond v1

- Real-time market data tier
- Custom scenario authoring UI
- Workspace Marketplace listing
- Tenant isolation for external clients
- Mobile companion app
- Custom alternative-data feeds (satellite analytics partners)
- Multi-language briefings (FR, ES, AR, PT)

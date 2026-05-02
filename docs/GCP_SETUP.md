# AtlasMind AI — Google Workspace + GCP Setup

This is the operator's runbook for standing AtlasMind AI up inside a Google Workspace organisation.

> Run these steps once, in order. After this, all changes are managed through Terraform in `infra/terraform/`.

---

## 0. Prerequisites

- A **Google Workspace** account (Business Standard or higher recommended; Enterprise required for VPC-SC + advanced controls).
- Billing account attached at the Workspace org level.
- A registered domain (e.g. `atlasmind.ai`) verified with Workspace.
- A Workspace **super-admin** running these steps.
- Local tools: `gcloud` CLI, `terraform >= 1.7`, `node >= 20`, `python >= 3.12`.

---

## 1. Workspace org & groups

In the Workspace admin console:

1. Confirm the org is verified (`atlasmind.ai`).
2. Create groups:
   - `eng@atlasmind.ai` — engineering team
   - `analysts@atlasmind.ai` — internal users running briefings
   - `briefings@atlasmind.ai` — external recipients of share links
   - `sec@atlasmind.ai` — security reviewers
3. In Drive admin: create a **shared drive** `AtlasMind / Briefings`. Owner = Workspace org. This is where generated Docs/Slides will live.
4. Reserve a service account naming convention: `*-sa@atlasmind-prod.iam.gserviceaccount.com`.

---

## 2. GCP organisation, folders, projects

1. Open Cloud Resource Manager in the Workspace org.
2. Create folder structure:
   ```
   AtlasMind/
     Production/
     Staging/
     Data/
     Shared/
   ```
3. Create projects:
   - `atlasmind-prod` under `Production/`
   - `atlasmind-stage` under `Staging/`
   - `atlasmind-data` under `Data/`
   - `atlasmind-shared` under `Shared/`
4. Link the billing account to all four projects.
5. Set labels on each project: `app=atlasmind`, `env=<prod|stage|data|shared>`, `cost_center=atlasmind`.

---

## 3. Enable APIs (per project)

Run from `infra/scripts/enable-apis.sh` (created in this repo):

For **`atlasmind-prod`** and **`atlasmind-stage`**:

```
aiplatform.googleapis.com           # Vertex AI
discoveryengine.googleapis.com      # Vertex AI Search / Agent Builder
run.googleapis.com                  # Cloud Run
cloudfunctions.googleapis.com
cloudscheduler.googleapis.com
pubsub.googleapis.com
bigquery.googleapis.com
firestore.googleapis.com
firebase.googleapis.com
firebasehosting.googleapis.com
identitytoolkit.googleapis.com
storage.googleapis.com
artifactregistry.googleapis.com
cloudbuild.googleapis.com
secretmanager.googleapis.com
iap.googleapis.com
docs.googleapis.com
slides.googleapis.com
sheets.googleapis.com
drive.googleapis.com
maps-backend.googleapis.com
earthengine.googleapis.com
trends.googleapis.com               # if/when promoted from research API
youtube.googleapis.com
logging.googleapis.com
monitoring.googleapis.com
cloudtrace.googleapis.com
```

For **`atlasmind-data`**: same minus Firebase + Run.

For **`atlasmind-shared`**: artifactregistry, cloudbuild, secretmanager, logging.

---

## 4. Identity & access (IAM)

Principle: **no humans with primitive roles, no service-account keys**.

Bind groups to roles:

| Group | Project | Role |
|---|---|---|
| `eng@atlasmind.ai` | shared, stage | Editor (limited; via custom role) |
| `eng@atlasmind.ai` | prod | Viewer |
| `sec@atlasmind.ai` | all | Security Reviewer + Logging Viewer |
| `analysts@atlasmind.ai` | prod | Custom role `atlasmind.runUser` |

Custom role `atlasmind.runUser` (defined in `infra/terraform/iam.tf`) allows:
- Calling the API gateway
- Reading Looker Studio dashboards
- Reading Drive briefings shared with the group

Service accounts (created by Terraform):

| SA | Purpose |
|---|---|
| `conductor-sa@` | Strategy Conductor Cloud Run service |
| `agent-geopol-sa@` … `agent-briefing-sa@` | One per agent |
| `ingest-sa@` | Ingestion functions/jobs |
| `api-sa@` | API gateway |
| `frontend-sa@` | Firebase backend functions |

Each agent SA gets **only** the BigQuery datasets, Pub/Sub topics, Secret Manager secrets, and Vertex AI endpoints it needs.

---

## 5. Networking & VPC Service Controls

1. Create a **VPC** `atlasmind-vpc` in `atlasmind-prod` and `atlasmind-data` with private subnets.
2. Cloud Run, Functions, and BigQuery use **Private Google Access**.
3. Create a **VPC Service Controls perimeter** wrapping `atlasmind-prod` + `atlasmind-data`. Allowed services: BigQuery, Storage, Vertex AI, Pub/Sub, Secret Manager, Logging.
4. Add `analysts@atlasmind.ai` to the access-level `internal-users` so they can hit the API from Workspace IPs.

---

## 6. BigQuery

Datasets in `atlasmind-prod` (multi-region `EU`):

| Dataset | Purpose |
|---|---|
| `atlasmind_warehouse` | Normalised analytical tables |
| `atlasmind_claims` | Every emitted agent claim |
| `atlasmind_runs` | Run metadata |
| `atlasmind_eval` | Eval golden sets and run scores |
| `atlasmind_scores` | Score history |

Same shape in `atlasmind-stage` for staging.

Provision via `infra/terraform/bigquery.tf`.

---

## 7. Cloud Storage

Buckets:

| Bucket | Lifecycle |
|---|---|
| `atlasmind-raw` | 90-day Archive after ingest, source-of-truth raw payloads |
| `atlasmind-runs` | Per-run artefacts; 30-day Coldline |
| `atlasmind-templates` | Doc/Slides/Sheets templates (versioned) |
| `atlasmind-build` | Cloud Build cache |

---

## 8. Vertex AI

1. In `atlasmind-prod`, enable **Vertex AI Agent Builder**.
2. Create a **Vertex AI Search datastore** `atlasmind-knowledge` with:
   - Source: `gs://atlasmind-raw/knowledge/`
   - Schema: unstructured docs with metadata `source`, `country`, `as_of`.
3. Create one **Agent Builder agent** per AtlasMind agent (8 total) wired to its Cloud Run service via OpenAPI spec.
4. Define the **Strategy Conductor** as a multi-agent orchestrator (ADK).

---

## 9. Firebase

1. Add Firebase to `atlasmind-prod`.
2. Enable **Authentication** with Google as the only provider, restricted to `atlasmind.ai` (and any client domains the user adds).
3. Create **Firestore** in native mode, region `eur3`.
4. Set up **Firebase Hosting** site `atlasmind`.
5. Connect to GitHub for preview channels (optional).

---

## 10. Workspace API access (Docs / Slides / Sheets / Drive)

Two paths:

**Internal users (atlasmind.ai)**
- Workspace admin grants **domain-wide delegation** to the briefing service account `briefing-sa@atlasmind-prod`.
- Scopes: `docs`, `slides`, `sheets`, `drive.file`.

**External clients on their own Workspace**
- Per-user **OAuth** consent flow at sign-up. Refresh tokens stored in Secret Manager (one secret per user).

Briefings are always written into the **client's** Drive, never AtlasMind's.

---

## 11. Cloud Build CI/CD

1. Connect repo `mintenance-ltd/atlasmind-ai` to Cloud Build in `atlasmind-shared`.
2. Triggers (configured by `infra/cloudbuild/`):
   - On push to `main`: build all containers, push to Artifact Registry.
   - On push to `release/*`: deploy to stage.
   - Manual gate: promote to prod.
3. Cloud Build SA needs: Cloud Run admin (stage), Artifact Registry writer, Secret Manager accessor.

---

## 12. Secrets

`atlasmind-shared` Secret Manager holds:

- `oauth_client_id` / `oauth_client_secret` (Workspace external OAuth app)
- `acled_api_key` (if licensed)
- `youtube_api_key`
- `maps_platform_api_key`
- Per-user OAuth refresh tokens (named `user_oauth/<sub>`)

Agent SAs are granted `secretAccessor` only to the secrets they need.

---

## 13. First deploy

```bash
# from repo root
cd infra/terraform
terraform init -backend-config=backend.prod.hcl
terraform workspace select prod
terraform apply

# build images
gcloud builds submit --config infra/cloudbuild/build-all.yaml

# deploy services
gcloud run deploy atlasmind-conductor --image=...   # via terraform in practice

# seed BigQuery from public datasets
python -m data.ingestion.seed --project atlasmind-prod
```

---

## 14. Post-setup smoke test

1. Sign in to the dashboard with a Workspace account.
2. Submit a run for `country=COG, horizon=24m`.
3. Confirm:
   - Pub/Sub `runs.requested` shows the message.
   - Cloud Trace shows 8 spans (one per agent).
   - BigQuery `atlasmind_claims` has rows for that `run_id`.
   - Drive `Briefings/COG/<run_id>/` contains a Doc, Slides deck, and Sheet.
   - Looker Studio dashboard renders the seven scores.

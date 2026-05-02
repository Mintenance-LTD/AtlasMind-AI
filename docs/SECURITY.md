# AtlasMind AI — Security & Responsible-Use Posture

AtlasMind AI handles sensitive country, market, and investment information. The following posture is mandatory.

---

## 1. Identity

- All human access is via **Google Workspace SSO**.
- Two-step verification is enforced for `eng@`, `sec@`, and admin accounts (Workspace policy).
- No long-lived service-account keys. Service-to-service auth uses **Workload Identity** + IAM tokens.
- External clients access the platform only through their own Workspace SSO; AtlasMind never holds passwords.

---

## 2. Network perimeter

- A **VPC Service Controls** perimeter wraps `atlasmind-prod` and `atlasmind-data`.
- Allowed-from list: Workspace-managed devices on the corporate access level, plus the Cloud Build SA.
- Cloud Run services are deployed with `--ingress=internal-and-cloud-load-balancing` and fronted by **IAP**.
- BigQuery, Cloud Storage, Vertex AI, Pub/Sub, and Secret Manager are inside the perimeter.

---

## 3. Data classification

| Class | Examples | Storage rules |
|---|---|---|
| **Public** | World Bank WDI, IMF WEO, GDELT | `atlasmind_warehouse`, no extra controls |
| **Restricted** | ACLED (licensed), private investor letters | Tagged dataset, IAM-restricted |
| **User** | User watchlists, saved briefings | Firestore + Drive in user's own Workspace |
| **Secret** | API keys, OAuth refresh tokens | Secret Manager only; never in BigQuery |

A `data_class` label is required on every BigQuery dataset; CI rejects new datasets without it.

---

## 4. Citation discipline

- Every agent claim must carry at least one source URL with an `as_of` date.
- The `core/tools/citations.py` validator rejects claim payloads with empty evidence.
- The Strategy Briefing Agent's system prompt forbids:
  - Unhedged predictions ("X *will* happen")
  - Specific listed-security recommendations
  - Personal financial advice
  - Speculative claims about named individuals' intentions

These rules are enforced both in the prompt and by a post-generation policy check (regex + Gemini classifier).

---

## 5. Logging & audit

- **Admin Activity** + **Data Access** audit logs are enabled on all four projects.
- A central **Logs Sink** in `atlasmind-shared` exports to BigQuery dataset `atlasmind_audit_logs`.
- Every agent run writes a structured log line with `run_id`, `agent`, `tool_calls[]`, `tokens_in`, `tokens_out`, `cost_usd_estimate`.
- Drive operations performed by the briefing SA are auditable in the Workspace admin console.

---

## 6. Responsible-use guardrails

- **Country sensitivity flag**: countries on a configurable "high-sensitivity" list (sanctions, active conflict) trigger a banner in the UI and a stricter prompt: more conservative confidence bands, mandatory dual-source citation.
- **No personal targeting**: agents are forbidden from producing dossiers on private individuals. Public officials may be discussed only in their official capacity, with sources.
- **No dual-use uplift**: agents refuse weapon-targeting, evasion, or operational planning queries — even when phrased as "research".
- **Output watermarking**: every Doc/Slides briefing carries a footer with `run_id`, `as_of`, and the line *"AtlasMind AI — decision-support analysis, not investment advice."*

---

## 7. Secret handling

- All secrets live in **Secret Manager** in `atlasmind-shared`.
- Rotation is automated where the upstream provider supports it (e.g. Maps Platform key, OAuth client secret).
- Per-user OAuth refresh tokens are stored under `secrets/user_oauth/<sub>` with a 30-day rotation review.
- A monthly **secret access audit** runs as a scheduled query against the audit-logs BigQuery dataset; anomalies post to the `sec@` group.

---

## 8. Supply-chain security

- All container images are built by Cloud Build inside `atlasmind-shared`, signed with **Binary Authorization**.
- Cloud Run services are configured to require attested images.
- Python dependencies are pinned (`uv.lock` / `requirements.lock`) and scanned by **Artifact Analysis**.
- Frontend dependencies are scanned by GitHub's Dependabot mirror — no direct `npm install` in CI without a lockfile.

---

## 9. Data residency

- Default region: **EU (`europe-west1` or `eur3` multi-region)**.
- Earth Engine and Vertex AI use multi-region endpoints; choose `eu` where available.
- Clients with stricter residency needs can request a dedicated tenant project — a v2 feature.

---

## 10. Incident response

- The `sec@atlasmind.ai` group receives Cloud Logging-based alerts on:
  - IAM role grants outside Terraform
  - VPC-SC violations
  - Anomalous Drive permission changes by `briefing-sa@`
  - Spending anomalies
- Runbooks live in `docs/runbooks/` (added in v1.1).

---

## 11. Privacy

- AtlasMind does not collect PII beyond Workspace identities.
- User watchlists and saved briefings are scoped to the user's organisation and deletable on request.
- The AtlasMind app's data-handling is documented in a Workspace Marketplace listing for any external users.

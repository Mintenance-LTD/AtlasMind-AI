# AtlasMind AI — Agent Specifications

Eight agents. Each one is a Cloud Run service powered by Gemini 2.5 (Pro for reasoning, Flash for high-volume signal classification), wrapped as a Vertex AI Agent Builder agent so the Strategy Conductor can call them through ADK's agent-to-agent protocol.

All agents follow the same input/output contract (see [`TECH_PACK.md` §7](TECH_PACK.md)).

---

## 1. Geopolitical Agent

**Purpose**  Track political risk, conflict, alliances, sanctions, and election cycles for a given country or region.

**Inputs**  `country` (ISO-3), optional `region`, `horizon_months`.

**Tools**
- BigQuery: `atlasmind_warehouse.governance_indicators`, `world_bank_wgi`, `acled_events`
- Vertex AI Search: policy + IMF Article IV index
- Google Search grounding (live news)
- Election calendar dataset (`atlasmind_warehouse.elections`)

**Output claims (examples)**
- "Election in Q3 2026 introduces near-term policy uncertainty (confidence: high)."
- "Sanction exposure has narrowed since 2024 (confidence: medium)."
- "Conflict density along northern corridor up 18% YoY (confidence: high)."

**Score produced**  `political_risk` (0–100, higher = more risk).

**Score formula (v1)**
```
political_risk = 0.30 * governance_inverse
               + 0.20 * conflict_intensity
               + 0.15 * election_proximity
               + 0.15 * sanctions_exposure
               + 0.10 * inflation_pressure
               + 0.10 * leadership_concentration
```

---

## 2. Market Agent

**Purpose**  Read the macro and market regime: equities, FX, rates, commodities, inflation, growth.

**Inputs**  `country`, optional `sector`, `horizon_months`.

**Tools**
- BigQuery: `atlasmind_warehouse.fx_rates`, `equity_indices`, `commodity_prices`, `policy_rates`, `inflation`, `current_account`
- IMF / OECD reference series via BigQuery
- Vertex AI Search: central bank releases, broker macro notes (where licensed)

**Output claims**
- "Local currency under sustained pressure; 12-month real depreciation ~14% (confidence: high)."
- "Policy rate expected to stay restrictive through 2026H1 (confidence: medium)."
- "Construction inputs (cement, rebar) up 9% YoY in USD (confidence: high)."

**Score produced**  `market_opportunity` (0–100).

---

## 3. Investment Agent

**Purpose**  Rank investment opportunities for the scope, with rationale and risk.

**Inputs**  All upstream agent outputs in the run.

**Tools**
- Internal scoring library (`core.scoring.investment`)
- BigQuery: `atlasmind_warehouse.sector_growth`, `vc_deals`, `gov_capex`
- Vertex AI Search: investor letters, sovereign wealth fund disclosures

**Output claims**
- "Solar mini-grid + storage scores 78/100 — high demand, low competition, medium regulatory risk."
- "Affordable housing (urban infill) scores 71/100 — high demand, high capital intensity, medium currency risk."

**Output table**  `opportunities` — top 10 ranked, each with: thesis, sector, capex band, time-to-revenue, key risks, key catalysts, confidence.

**Score produced**  `investment_readiness` (0–100, country-level).

**Hard rule**  *Never* recommend a specific listed security. Recommendations are at the **theme/sector** level. The system prompt enforces this.

---

## 4. Population Agent

**Purpose**  Read demographics, migration, urbanisation, labour-force structure, education and income trends.

**Inputs**  `country`, optional `sub_region`.

**Tools**
- BigQuery: UN Population Division, World Bank WDI, national stats office tables
- Earth Engine: `WorldPop` urban-extent change, `VIIRS` night-lights
- Maps Platform: city footprints

**Output claims**
- "Median age 19.2; 60% under 25 (confidence: high)."
- "Brazzaville urban footprint expanded ~6% in 5 years (confidence: high)."
- "Labour-force participation among urban women up 4 pp since 2020 (confidence: medium)."

**Score produced**  `demographic_growth` (0–100).

---

## 5. Technology Trend Agent

**Purpose**  Surface emerging app, AI, software, and consumer-attention trends — globally and per region.

**Inputs**  Optional `region`, optional `theme`.

**Tools**
- BigQuery: Google Trends public dataset, GitHub Archive, Stack Overflow, patent filings
- YouTube Data API
- Play Store / App Store category snapshots (loaded into BigQuery)
- Vertex AI Search: Product Hunt, startup announcements

**Output claims**
- "Surge in 'agent' search interest sustained for 18 months — not a fad (confidence: high)."
- "Construction-tech inspection apps growing >40% YoY in MENA + Sub-Saharan Africa (confidence: medium)."
- "Local-language LLM downloads in Francophone Africa up 5x YTD (confidence: medium)."

**Score produced**  `technology_adoption` (0–100, country-level).

---

## 6. Country Risk Agent

**Purpose**  Produce one nation-level scorecard combining governance, economic, demographic, and security signals.

**Inputs**  Outputs of Geopolitical, Market, Population (+ governance reference data).

**Tools**
- BigQuery: `world_bank_wgi`, `transparency_cpi`, `freedom_house`, `imf_debt`
- Internal scoring library (`core.scoring.country_risk`)

**Output**  Country Risk Scorecard with the seven AtlasMind scores, plus `infrastructure_gap` and `strategic_importance`.

**Score produced**  Composite `country_risk` (0–100), plus the seven dimension scores.

**Score formula sketch (v1)**
```
country_risk = 0.25 * political_risk
             + 0.20 * macro_stress         (inverse of market_opportunity stability)
             + 0.15 * institutional_quality_inv
             + 0.15 * external_balance_stress
             + 0.10 * security_environment
             + 0.10 * debt_burden
             + 0.05 * climate_exposure
```

---

## 7. Scenario Agent

**Purpose**  Generate three named scenarios — usually `Base`, `Upside`, `Stress` — with probabilities, drivers, and the *early-warning indicators* that distinguish them.

**Inputs**  All upstream agent outputs.

**Tools**
- Internal scoring library
- Gemini 2.5 Pro for narrative composition
- BigQuery: historical analogues table

**Output claims**
- "Base (55%): muddle-through; growth 3.5%; FX depreciates 8%."
- "Upside (20%): infra unlock + commodity tailwind; growth 6%."
- "Stress (25%): election dispute + currency shock; recession risk."

Each scenario lists 3–6 **trigger indicators** that the user can monitor, e.g. *"FX reserves drop below 3 months of imports"*, *"opposition refuses certified result"*.

**Score produced**  None — scenarios are qualitative but evidence-bound.

---

## 8. Strategy Briefing Agent

**Purpose**  Synthesise everything into board-grade outputs delivered into the user's Google Drive.

**Inputs**  All upstream agent outputs.

**Tools**
- Google Docs API (executive brief from template)
- Google Slides API (board deck from template)
- Google Sheets API (opportunity scorecard)
- Drive API (file placement, sharing)
- Looker Studio link generator

**Outputs**
- `Brief_<country>_<run_id>.docx` (Doc) — 1 page
- `BoardPack_<country>_<run_id>.gslides` — 8–12 slides
- `Scorecard_<country>_<run_id>.gsheet`
- Heat-map and opportunity-map links

**Hard rules in the system prompt**
- Every claim cites at least one source.
- No unhedged predictions.
- No instrument-level financial advice.
- All outputs include the run's `as_of` timestamp and the confidence band.
- Every figure includes a unit and a date.

---

## Score catalogue

| Score | Range | Higher means | Owning agent |
|---|---|---|---|
| `political_risk` | 0–100 | Riskier | Geopolitical |
| `market_opportunity` | 0–100 | More opportunity | Market |
| `investment_readiness` | 0–100 | More ready | Investment |
| `demographic_growth` | 0–100 | Stronger demographic tailwind | Population |
| `technology_adoption` | 0–100 | Faster tech adoption | Technology Trend |
| `infrastructure_gap` | 0–100 | Bigger gap (= more opportunity if capital available) | Country Risk |
| `strategic_importance` | 0–100 | Higher global strategic relevance | Country Risk |

A composite `country_risk` and a composite `country_opportunity` are computed by the Country Risk Agent for ranking.

---

## Eval

Each agent has a golden set under `eval/<agent>/` with:
- `inputs.jsonl` — past runs
- `golden.jsonl` — accepted outputs
- `rubric.md` — the scoring rubric

Nightly evaluation uses Vertex AI Eval Service against the rubric and posts results to Looker Studio. Regressions block promotion from stage to prod.

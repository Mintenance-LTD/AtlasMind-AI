"""Population Agent.

Reads demographic indicators from BigQuery, composes citation-bound claims,
computes the demographic_growth score, and returns an AtlasMind AgentResult.

Data sources used by v1:
  - World Bank WDI    (population, urban share & growth, age structure,
                       LFPR, life expectancy, secondary completion)
  - Earth Engine      (urban-extent change — wired but optional)

See docs/AGENTS.md §4.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from core.runtime import AgentRunner
from core.schemas import AgentResult, Claim, Confidence, Evidence, RunRequest
from core.scoring import (
    SCORE_VERSION,
    demographic_growth_score,
    normalise_education,
    normalise_lfpr,
    normalise_life_expectancy,
    normalise_population_growth,
    normalise_urban_growth,
    normalise_youth_share,
)
from core.tools import BigQueryTool, EarthEngineTool


WDI = {
    "population_total":   "SP.POP.TOTL",
    "population_growth":  "SP.POP.GROW",
    "urban_share":        "SP.URB.TOTL.IN.ZS",
    "urban_growth":       "SP.URB.GROW",
    "share_0_14":         "SP.POP.0014.TO.ZS",
    "share_15_64":        "SP.POP.1564.TO.ZS",
    "lfpr":               "SL.TLF.CACT.ZS",
    "life_expectancy":    "SP.DYN.LE00.IN",
    "secondary_complete": "SE.SEC.CMPT.LO.ZS",
}

WDI_PORTAL = "https://data.worldbank.org/indicator"


class PopulationAgent(AgentRunner):
    name = "population"

    def __init__(self, bq: BigQueryTool | None = None, ee: EarthEngineTool | None = None) -> None:
        super().__init__()
        self.bq = bq or BigQueryTool()
        self.ee = ee or EarthEngineTool()

    async def run(self, request: RunRequest) -> AgentResult:
        country = (request.scope.country or "").upper()
        if not country:
            return self._empty(request, "no country in scope")

        rows = await self.bq.wdi_indicators(country, list(WDI.values()))
        if not rows:
            return self._empty(request, f"no WDI data for {country}")

        claims = list(self._compose_claims(rows))
        score = self._score(rows)

        return AgentResult(
            run_id=request.run_id,
            agent=self.name,
            as_of=datetime.now(UTC),
            claims=claims,
            scores={"demographic_growth": score},
            notes=f"score_version={SCORE_VERSION}; indicators={len(rows)}/{len(WDI)}",
        )

    # ------------------------------------------------------------------ claims

    def _compose_claims(self, rows: dict[str, dict[str, Any]]) -> list[Claim]:
        claims: list[Claim] = []
        ev_for = lambda code: Evidence(  # noqa: E731
            source=f"World Bank WDI · {code}",
            url=f"{WDI_PORTAL}/{code}",
            as_of=datetime(rows[code]["year"], 1, 1, tzinfo=UTC),
        )

        if WDI["population_total"] in rows and WDI["population_growth"] in rows:
            pop = rows[WDI["population_total"]]
            growth = rows[WDI["population_growth"]]
            claims.append(
                Claim(
                    statement=(
                        f"Population stands at {pop['value']:,.0f} "
                        f"({pop['year']}), growing {growth['value']:.2f}% per year."
                    ),
                    confidence=Confidence.HIGH,
                    evidence=[ev_for(WDI["population_total"]), ev_for(WDI["population_growth"])],
                    tags=["demographics", "population"],
                )
            )

        if WDI["urban_share"] in rows and WDI["urban_growth"] in rows:
            ushare = rows[WDI["urban_share"]]
            ugrowth = rows[WDI["urban_growth"]]
            claims.append(
                Claim(
                    statement=(
                        f"{ushare['value']:.1f}% of the population is urban "
                        f"({ushare['year']}); urban population is growing "
                        f"{ugrowth['value']:.2f}% per year."
                    ),
                    confidence=Confidence.HIGH,
                    evidence=[ev_for(WDI["urban_share"]), ev_for(WDI["urban_growth"])],
                    early_warning=[
                        "Urban growth above 4% sustained → housing & infrastructure stress",
                    ],
                    tags=["urbanisation"],
                )
            )

        if WDI["share_0_14"] in rows and WDI["share_15_64"] in rows:
            youth = rows[WDI["share_0_14"]]["value"] + 0.4 * rows[WDI["share_15_64"]]["value"]
            claims.append(
                Claim(
                    statement=(
                        f"Approximately {youth:.0f}% of the population is under 25 — "
                        "a large youth cohort indicating long-term labour-force expansion."
                    ),
                    confidence=Confidence.MEDIUM,  # composite of two indicators
                    evidence=[ev_for(WDI["share_0_14"]), ev_for(WDI["share_15_64"])],
                    early_warning=[
                        "Youth unemployment > 25% sustained → social-stability risk",
                    ],
                    tags=["age_structure", "labour"],
                )
            )

        if WDI["lfpr"] in rows:
            lfpr = rows[WDI["lfpr"]]
            claims.append(
                Claim(
                    statement=(
                        f"Labour-force participation is {lfpr['value']:.1f}% ({lfpr['year']})."
                    ),
                    confidence=Confidence.HIGH,
                    evidence=[ev_for(WDI["lfpr"])],
                    tags=["labour"],
                )
            )

        if WDI["life_expectancy"] in rows:
            le = rows[WDI["life_expectancy"]]
            claims.append(
                Claim(
                    statement=f"Life expectancy at birth is {le['value']:.1f} years ({le['year']}).",
                    confidence=Confidence.HIGH,
                    evidence=[ev_for(WDI["life_expectancy"])],
                    tags=["health"],
                )
            )

        if WDI["secondary_complete"] in rows:
            sec = rows[WDI["secondary_complete"]]
            claims.append(
                Claim(
                    statement=(
                        f"Lower-secondary completion rate is {sec['value']:.0f}% "
                        f"({sec['year']}); a key constraint on labour productivity."
                    ),
                    confidence=Confidence.MEDIUM if sec["year"] < 2020 else Confidence.HIGH,
                    evidence=[ev_for(WDI["secondary_complete"])],
                    tags=["education"],
                )
            )

        return claims

    # ------------------------------------------------------------------ score

    def _score(self, rows: dict[str, dict[str, Any]]) -> float:
        inputs: dict[str, float] = {}
        if WDI["population_growth"] in rows:
            inputs["population_growth"] = normalise_population_growth(
                rows[WDI["population_growth"]]["value"]
            )
        if WDI["urban_growth"] in rows:
            inputs["urban_growth"] = normalise_urban_growth(
                rows[WDI["urban_growth"]]["value"]
            )
        if WDI["share_0_14"] in rows and WDI["share_15_64"] in rows:
            youth_pct = (
                rows[WDI["share_0_14"]]["value"] + 0.4 * rows[WDI["share_15_64"]]["value"]
            )
            inputs["youth_share"] = normalise_youth_share(youth_pct)
        if WDI["lfpr"] in rows:
            inputs["labour_force_participation"] = normalise_lfpr(
                rows[WDI["lfpr"]]["value"]
            )
        if WDI["life_expectancy"] in rows:
            inputs["life_expectancy"] = normalise_life_expectancy(
                rows[WDI["life_expectancy"]]["value"]
            )
        if WDI["secondary_complete"] in rows:
            inputs["education_attainment"] = normalise_education(
                rows[WDI["secondary_complete"]]["value"]
            )
        return demographic_growth_score(inputs)  # type: ignore[arg-type]

    # ------------------------------------------------------------------ helpers

    def _empty(self, request: RunRequest, note: str) -> AgentResult:
        return AgentResult(
            run_id=request.run_id,
            agent=self.name,
            as_of=datetime.now(UTC),
            claims=[],
            scores={"demographic_growth": 0.0},
            notes=note,
        )

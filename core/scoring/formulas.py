"""Score formulas. Versioned weights live here. See docs/AGENTS.md §scoring.

Every score is 0-100. Higher = more of whatever the score measures
(more risk, more opportunity, more tailwind). Scores are computed from
*normalised* inputs already on a 0-100 scale — the agents do their own
normalisation from raw data and document it in claim evidence.
"""

from __future__ import annotations

from typing import TypedDict


SCORE_VERSION = "v1.0"


class PoliticalRiskInputs(TypedDict, total=False):
    governance_inverse: float
    conflict_intensity: float
    election_proximity: float
    sanctions_exposure: float
    inflation_pressure: float
    leadership_concentration: float


class CountryRiskInputs(TypedDict, total=False):
    political_risk: float
    macro_stress: float
    institutional_quality_inv: float
    external_balance_stress: float
    security_environment: float
    debt_burden: float
    climate_exposure: float


class DemographicGrowthInputs(TypedDict, total=False):
    population_growth: float           # 0-100 (already normalised)
    urban_growth: float                # 0-100
    youth_share: float                 # 0-100 (% under 25, capped at 60)
    labour_force_participation: float  # 0-100
    life_expectancy: float             # 0-100 (mapped from years)
    education_attainment: float        # 0-100


SCORE_WEIGHTS: dict[str, dict[str, float]] = {
    "political_risk": {
        "governance_inverse": 0.30,
        "conflict_intensity": 0.20,
        "election_proximity": 0.15,
        "sanctions_exposure": 0.15,
        "inflation_pressure": 0.10,
        "leadership_concentration": 0.10,
    },
    "country_risk": {
        "political_risk": 0.25,
        "macro_stress": 0.20,
        "institutional_quality_inv": 0.15,
        "external_balance_stress": 0.15,
        "security_environment": 0.10,
        "debt_burden": 0.10,
        "climate_exposure": 0.05,
    },
    "demographic_growth": {
        "population_growth": 0.20,
        "urban_growth": 0.20,
        "youth_share": 0.20,
        "labour_force_participation": 0.15,
        "life_expectancy": 0.15,
        "education_attainment": 0.10,
    },
}


def _weighted(weights: dict[str, float], inputs: dict[str, float]) -> float:
    """Weighted average over inputs that are present.

    Re-normalises by the sum of weights actually used, so a country with
    partial data still gets a defensible score (the missing inputs are
    just absent, not assumed zero).
    """
    total = 0.0
    used = 0.0
    for key, w in weights.items():
        if key in inputs:
            total += w * max(0.0, min(100.0, inputs[key]))
            used += w
    if used == 0:
        return 0.0
    return round(total / used, 2)


def political_risk_score(inputs: PoliticalRiskInputs) -> float:
    return _weighted(SCORE_WEIGHTS["political_risk"], dict(inputs))


def country_risk_score(inputs: CountryRiskInputs) -> float:
    return _weighted(SCORE_WEIGHTS["country_risk"], dict(inputs))


def demographic_growth_score(inputs: DemographicGrowthInputs) -> float:
    return _weighted(SCORE_WEIGHTS["demographic_growth"], dict(inputs))


# --- Normalisers used by the Population Agent ------------------------------


def normalise_population_growth(annual_pct: float) -> float:
    """Map annual population growth % to 0-100. 0% -> 0, 3.5% -> 100, capped."""
    return max(0.0, min(100.0, (annual_pct / 3.5) * 100.0))


def normalise_urban_growth(annual_pct: float) -> float:
    """Urban growth tends to run higher than total. 5% -> 100."""
    return max(0.0, min(100.0, (annual_pct / 5.0) * 100.0))


def normalise_youth_share(pct_under_25: float) -> float:
    """50% under 25 -> ~83. 60% under 25 -> 100."""
    return max(0.0, min(100.0, (pct_under_25 / 60.0) * 100.0))


def normalise_lfpr(pct: float) -> float:
    """Labour force participation rate is already 0-100."""
    return max(0.0, min(100.0, pct))


def normalise_life_expectancy(years: float) -> float:
    """50y -> 0, 85y -> 100. Below 50 floored, above 85 capped."""
    return max(0.0, min(100.0, ((years - 50.0) / 35.0) * 100.0))


def normalise_education(secondary_completion_pct: float) -> float:
    return max(0.0, min(100.0, secondary_completion_pct))

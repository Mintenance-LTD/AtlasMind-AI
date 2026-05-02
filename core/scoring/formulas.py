"""Score formulas. Versioned weights live here. See docs/AGENTS.md §scoring."""

from __future__ import annotations

from typing import TypedDict


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
}


def _weighted(weights: dict[str, float], inputs: dict[str, float]) -> float:
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

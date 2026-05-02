from core.scoring import (
    country_risk_score,
    demographic_growth_score,
    normalise_life_expectancy,
    normalise_population_growth,
    normalise_urban_growth,
    normalise_youth_share,
    political_risk_score,
)


def test_political_risk_basic() -> None:
    score = political_risk_score(
        {
            "governance_inverse": 60,
            "conflict_intensity": 40,
            "election_proximity": 80,
            "sanctions_exposure": 20,
            "inflation_pressure": 50,
            "leadership_concentration": 70,
        }
    )
    assert 0 <= score <= 100


def test_country_risk_uses_provided_inputs_only() -> None:
    s = country_risk_score({"political_risk": 50, "macro_stress": 30})
    assert 0 < s < 100


def test_demographic_growth_full_inputs() -> None:
    score = demographic_growth_score(
        {
            "population_growth": 70,
            "urban_growth": 64,
            "youth_share": 80,
            "labour_force_participation": 65,
            "life_expectancy": 50,
            "education_attainment": 60,
        }
    )
    assert 0 <= score <= 100


def test_demographic_growth_partial_inputs() -> None:
    score = demographic_growth_score({"population_growth": 60, "urban_growth": 70})
    assert 0 < score <= 100


def test_normalisers_clip_outside_range() -> None:
    assert normalise_population_growth(-1) == 0.0
    assert normalise_population_growth(10) == 100.0
    assert normalise_urban_growth(20) == 100.0
    assert normalise_youth_share(75) == 100.0
    assert normalise_life_expectancy(40) == 0.0
    assert normalise_life_expectancy(90) == 100.0

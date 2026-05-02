from core.scoring import country_risk_score, political_risk_score


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

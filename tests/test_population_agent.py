"""End-to-end test for the Population Agent against the fixture backend.

These tests assert agent contract (citation-bound claims, valid scores) and
guard against regressions in score weights or claim composition.
"""

import os
import uuid

import pytest

from core.schemas import Confidence, RunRequest, RunScope
from core.tools.citations import validate_claims

from agents.population.agent import PopulationAgent

os.environ.setdefault("ATLASMIND_BQ_BACKEND", "fixture")


def _request(country: str) -> RunRequest:
    return RunRequest(
        run_id=str(uuid.uuid4()),
        scope=RunScope(country=country, horizon_months=24),
        depth="standard",
        requested_by="pytest@atlasmind.local",
    )


@pytest.mark.parametrize("country", ["COG", "NGA", "KEN"])
async def test_population_agent_produces_citation_bound_claims(country: str) -> None:
    agent = PopulationAgent()
    result = await agent.run(_request(country))

    assert result.agent == "population"
    assert result.claims, f"no claims for {country}"
    validate_claims(result.claims)  # raises if any claim is unevidenced
    for c in result.claims:
        assert c.evidence, "every claim must carry evidence"
        for ev in c.evidence:
            assert ev.url is None or "worldbank.org" in str(ev.url)


@pytest.mark.parametrize("country", ["COG", "NGA", "KEN"])
async def test_population_agent_score_in_range(country: str) -> None:
    agent = PopulationAgent()
    result = await agent.run(_request(country))
    score = result.scores["demographic_growth"]
    assert 0.0 <= score <= 100.0
    assert score > 0.0, "fixture data should yield a non-zero score"


async def test_population_agent_scores_kenya_higher_than_nigeria() -> None:
    """Sanity check: Kenya's 76.6% LFPR + 79% secondary completion vs.
    Nigeria's 53.4% / 73% should give Kenya the higher demographic_growth score
    under v1 weights. Catches accidental weight regressions."""
    agent = PopulationAgent()
    nga = (await agent.run(_request("NGA"))).scores["demographic_growth"]
    ken = (await agent.run(_request("KEN"))).scores["demographic_growth"]
    assert ken > nga, f"expected KEN({ken}) > NGA({nga})"


async def test_population_agent_handles_missing_country_gracefully() -> None:
    agent = PopulationAgent()
    result = await agent.run(_request("XYZ"))  # not in fixtures
    assert result.scores["demographic_growth"] == 0.0
    assert result.claims == []
    assert "no WDI data" in (result.notes or "")

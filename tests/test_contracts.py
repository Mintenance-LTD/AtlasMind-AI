"""Sanity tests for the cross-agent contract."""

from datetime import UTC, datetime

import pytest

from core.schemas import AgentResult, Claim, Confidence, Evidence, RunRequest, RunScope
from core.tools.citations import CitationError, validate_claims


def _claim() -> Claim:
    return Claim(
        statement="GDP growth accelerated to 4.1% in 2025 (estimate).",
        confidence=Confidence.MEDIUM,
        evidence=[Evidence(source="IMF WEO", as_of=datetime.now(UTC))],
    )


def test_run_request_round_trip() -> None:
    req = RunRequest(
        run_id="r-1",
        scope=RunScope(country="COG", horizon_months=24),
        depth="standard",
        requested_by="user@atlasmind.ai",
    )
    assert req.scope.country == "COG"


def test_agent_result_validates() -> None:
    result = AgentResult(
        run_id="r-1",
        agent="market",
        as_of=datetime.now(UTC),
        claims=[_claim()],
        scores={"market_opportunity": 62.0},
    )
    assert result.scores["market_opportunity"] == 62.0


def test_citations_reject_unhedged_predictions() -> None:
    bad = Claim(
        statement="The currency will fall by 20% next year.",
        confidence=Confidence.HIGH,
        evidence=[Evidence(source="X", as_of=datetime.now(UTC))],
    )
    with pytest.raises(CitationError):
        validate_claims([bad])


def test_citations_require_evidence() -> None:
    with pytest.raises(Exception):
        Claim(
            statement="Some claim",
            confidence=Confidence.LOW,
            evidence=[],
        )

"""Citation discipline. No claim is allowed without evidence."""

from __future__ import annotations

from core.schemas import Claim


class CitationError(ValueError):
    """Raised when a claim violates citation rules."""


def validate_claims(claims: list[Claim]) -> None:
    """Hard rules enforced for every agent's output.

    Mirrors the policy described in docs/SECURITY.md §4.
    """
    for claim in claims:
        if not claim.evidence:
            raise CitationError(f"Claim has no evidence: {claim.statement!r}")
        for ev in claim.evidence:
            if not ev.source:
                raise CitationError(f"Evidence missing source for: {claim.statement!r}")
            if not ev.as_of:
                raise CitationError(f"Evidence missing as_of for: {claim.statement!r}")

        lower = claim.statement.lower()
        for forbidden in (" will rise", " will fall", "guaranteed to", "definitely will"):
            if forbidden in lower:
                raise CitationError(
                    f"Unhedged prediction not allowed: {claim.statement!r}"
                )

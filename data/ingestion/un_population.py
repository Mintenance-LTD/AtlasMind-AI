"""UN World Population Prospects ingestion."""

from __future__ import annotations

from typing import Any

from data.ingestion.base import IngestJob


class UNWPPIngest(IngestJob):
    source = "un_wpp"

    async def fetch(self) -> list[dict[str, Any]]:
        return []

    async def load(self, rows: list[dict[str, Any]]) -> int:
        return len(rows)

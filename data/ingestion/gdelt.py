"""GDELT 2.0 events — Goldstein scale, conflict density, country scoring."""

from __future__ import annotations

from typing import Any

from data.ingestion.base import IngestJob


class GDELTIngest(IngestJob):
    source = "gdelt"

    async def fetch(self) -> list[dict[str, Any]]:
        return []

    async def load(self, rows: list[dict[str, Any]]) -> int:
        return len(rows)

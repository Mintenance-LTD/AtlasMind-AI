"""Google Trends ingestion via the BigQuery public dataset."""

from __future__ import annotations

from typing import Any

from data.ingestion.base import IngestJob


class GoogleTrendsIngest(IngestJob):
    source = "google_trends"

    async def fetch(self) -> list[dict[str, Any]]:
        return []

    async def load(self, rows: list[dict[str, Any]]) -> int:
        return len(rows)

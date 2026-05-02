"""IMF WEO + Article IV ingestion."""

from __future__ import annotations

from typing import Any

from data.ingestion.base import IngestJob


class IMFWEOIngest(IngestJob):
    source = "imf_weo"

    async def fetch(self) -> list[dict[str, Any]]:
        return []

    async def load(self, rows: list[dict[str, Any]]) -> int:
        return len(rows)


class IMFArticleIVIngest(IngestJob):
    """Article IV PDFs land in gs://atlasmind-raw/knowledge/imf_article_iv/
    and are indexed by Vertex AI Search.
    """
    source = "imf_article_iv"

    async def fetch(self) -> list[dict[str, Any]]:
        return []

    async def load(self, rows: list[dict[str, Any]]) -> int:
        return len(rows)

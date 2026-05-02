"""Vertex AI Search — atlasmind-knowledge datastore."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import structlog

log = structlog.get_logger()


@dataclass
class VertexSearchTool:
    project: str
    location: str
    datastore: str = "atlasmind-knowledge"

    @classmethod
    def from_env(cls) -> VertexSearchTool:
        return cls(
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", "atlasmind-stage"),
            location=os.environ.get("VERTEX_LOCATION", "europe-west1"),
        )

    async def search(
        self,
        query: str,
        country_iso3: str | None = None,
        top_k: int = 8,
    ) -> list[dict[str, Any]]:
        log.info("search.query", q=query, country=country_iso3, top_k=top_k)
        return []

"""BigQuery tool — primary read path for every agent."""

from __future__ import annotations

import os
from typing import Any

import structlog

log = structlog.get_logger()


class BigQueryTool:
    """Wraps the BigQuery client with AtlasMind conventions.

    Real implementation will use google-cloud-bigquery; the surface here is the
    contract every agent codes against.
    """

    def __init__(self, project: str | None = None) -> None:
        self.project = project or os.environ.get("GOOGLE_CLOUD_PROJECT", "atlasmind-stage")
        self.warehouse = os.environ.get("BQ_DATASET_WAREHOUSE", "atlasmind_warehouse")

    async def query(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        log.info("bq.query", project=self.project, params=list((params or {}).keys()))
        return []

    async def country_indicator(
        self, country_iso3: str, indicator: str, latest: bool = True
    ) -> dict[str, Any] | None:
        sql = f"""
            SELECT country_iso3, indicator, value, as_of, source
            FROM `{self.project}.{self.warehouse}.country_indicators`
            WHERE country_iso3 = @c AND indicator = @i
            {"ORDER BY as_of DESC LIMIT 1" if latest else "ORDER BY as_of"}
        """
        rows = await self.query(sql, {"c": country_iso3, "i": indicator})
        return rows[0] if rows else None

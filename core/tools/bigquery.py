"""BigQuery tool — primary read path for every agent.

Two backends:
  - "live"    : real google-cloud-bigquery client. Requires Application Default
                Credentials and a billable GCP project.
  - "fixture" : reads canned JSON from data/fixtures/. Lets agents and tests
                run with no creds at all.

Backend selection: env var ATLASMIND_BQ_BACKEND, defaults to "fixture" until
the GCP projects in docs/GCP_SETUP.md exist.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import structlog

log = structlog.get_logger()


WB_PUBLIC_DATASET = "bigquery-public-data.world_bank_wdi.indicators_data"


class BigQueryTool:
    def __init__(self, project: str | None = None, backend: str | None = None) -> None:
        self.project = project or os.environ.get("GOOGLE_CLOUD_PROJECT", "atlasmind-stage")
        self.warehouse = os.environ.get("BQ_DATASET_WAREHOUSE", "atlasmind_warehouse")
        self.backend = backend or os.environ.get("ATLASMIND_BQ_BACKEND", "fixture")
        self._client: Any | None = None
        self._fixtures_root = (
            Path(__file__).resolve().parents[2] / "data" / "fixtures" / "bigquery"
        )

    # ---- live -------------------------------------------------------------

    def _live_client(self) -> Any:
        if self._client is None:
            from google.cloud import bigquery  # type: ignore

            self._client = bigquery.Client(project=self.project)
        return self._client

    async def _live_query(
        self, sql: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        import asyncio

        from google.cloud import bigquery  # type: ignore

        client = self._live_client()
        job_params: list[Any] = []
        for k, v in (params or {}).items():
            if isinstance(v, list):
                job_params.append(bigquery.ArrayQueryParameter(k, "STRING", v))
            else:
                job_params.append(bigquery.ScalarQueryParameter(k, _bq_scalar_type(v), v))
        config = bigquery.QueryJobConfig(query_parameters=job_params)

        def _run() -> list[dict[str, Any]]:
            job = client.query(sql, job_config=config)
            return [dict(row) for row in job.result()]

        return await asyncio.to_thread(_run)

    # ---- fixture ----------------------------------------------------------

    async def _fixture_query(
        self, sql: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        log.warning("bq.fixture.raw_sql_unsupported")
        return []

    def _fixture_wdi(
        self, country_iso3: str, indicators: list[str]
    ) -> dict[str, dict[str, Any]]:
        path = self._fixtures_root / "wdi" / f"{country_iso3.upper()}.json"
        if not path.exists():
            log.warning("bq.fixture.miss", country=country_iso3, path=str(path))
            return {}
        with path.open() as f:
            data: dict[str, dict[str, Any]] = json.load(f)
        return {k: data[k] for k in indicators if k in data}

    # ---- public -----------------------------------------------------------

    async def query(
        self, sql: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        log.info("bq.query", project=self.project, backend=self.backend)
        if self.backend == "live":
            return await self._live_query(sql, params)
        return await self._fixture_query(sql, params)

    async def wdi_indicators(
        self,
        country_iso3: str,
        indicators: list[str],
    ) -> dict[str, dict[str, Any]]:
        """Latest value of each WDI indicator for a country.

        Returns ``{indicator_code: {"value": float, "year": int, "source": str}}``.
        """
        if self.backend == "fixture":
            return self._fixture_wdi(country_iso3, indicators)

        sql = f"""
            WITH ranked AS (
              SELECT
                country_code,
                indicator_code,
                value,
                year,
                ROW_NUMBER() OVER (
                  PARTITION BY country_code, indicator_code
                  ORDER BY year DESC
                ) AS rn
              FROM `{WB_PUBLIC_DATASET}`
              WHERE country_code = @c
                AND indicator_code IN UNNEST(@inds)
                AND value IS NOT NULL
            )
            SELECT indicator_code, value, year
            FROM ranked
            WHERE rn = 1
        """
        rows = await self._live_query(sql, {"c": country_iso3, "inds": indicators})
        return {
            r["indicator_code"]: {
                "value": float(r["value"]),
                "year": int(r["year"]),
                "source": "World Bank WDI",
            }
            for r in rows
        }


def _bq_scalar_type(value: Any) -> str:
    if isinstance(value, bool):
        return "BOOL"
    if isinstance(value, int):
        return "INT64"
    if isinstance(value, float):
        return "FLOAT64"
    return "STRING"

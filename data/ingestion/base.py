"""Base classes for ingestion jobs."""

from __future__ import annotations

import os
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import structlog

log = structlog.get_logger()


@dataclass
class IngestRun:
    ingest_id: str
    source: str
    as_of: datetime
    rows_in: int = 0
    rows_loaded: int = 0
    checksum: str = ""
    gcs_uri: str = ""
    status: str = "ok"


class IngestJob(ABC):
    """One ingest job per source. Schedule via Cloud Scheduler."""

    source: str = "unknown"

    def __init__(self) -> None:
        self.project = os.environ.get("GOOGLE_CLOUD_PROJECT", "atlasmind-stage")
        self.raw_bucket = os.environ.get("GCS_BUCKET_RAW", "atlasmind-raw")

    @abstractmethod
    async def fetch(self) -> list[dict[str, Any]]:
        """Pull from upstream and return rows."""

    @abstractmethod
    async def load(self, rows: list[dict[str, Any]]) -> int:
        """MERGE into atlasmind_warehouse.*; return rows_loaded."""

    async def run(self) -> IngestRun:
        run = IngestRun(
            ingest_id=str(uuid.uuid4()),
            source=self.source,
            as_of=datetime.now(UTC),
        )
        log.info("ingest.start", source=self.source, ingest_id=run.ingest_id)
        rows = await self.fetch()
        run.rows_in = len(rows)
        run.rows_loaded = await self.load(rows)
        log.info(
            "ingest.complete",
            source=self.source,
            ingest_id=run.ingest_id,
            rows_in=run.rows_in,
            rows_loaded=run.rows_loaded,
        )
        return run

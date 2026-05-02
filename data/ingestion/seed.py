"""One-shot seeder. Runs every ingest job once for first-time bootstrap.

    python -m data.ingestion.seed --project atlasmind-prod
"""

from __future__ import annotations

import argparse
import asyncio

import structlog

from data.ingestion.base import IngestJob
from data.ingestion.gdelt import GDELTIngest
from data.ingestion.google_trends import GoogleTrendsIngest
from data.ingestion.imf import IMFArticleIVIngest, IMFWEOIngest
from data.ingestion.un_population import UNWPPIngest
from data.ingestion.world_bank import WorldBankWDIIngest

log = structlog.get_logger()


JOBS: list[type[IngestJob]] = [
    WorldBankWDIIngest,
    IMFWEOIngest,
    IMFArticleIVIngest,
    UNWPPIngest,
    GoogleTrendsIngest,
    GDELTIngest,
]


async def main(project: str) -> None:
    log.info("seed.start", project=project, job_count=len(JOBS))
    for job_cls in JOBS:
        run = await job_cls().run()
        log.info("seed.job", job=job_cls.__name__, status=run.status)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()
    asyncio.run(main(args.project))

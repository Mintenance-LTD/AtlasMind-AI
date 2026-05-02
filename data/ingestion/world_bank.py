"""World Bank WDI loader."""

from __future__ import annotations

from typing import Any

from data.ingestion.base import IngestJob


class WorldBankWDIIngest(IngestJob):
    source = "worldbank_wdi"
    indicators: list[str] = [
        "NY.GDP.MKTP.CD",       # GDP, current US$
        "NY.GDP.MKTP.KD.ZG",    # GDP growth (annual %)
        "FP.CPI.TOTL.ZG",       # Inflation, consumer prices
        "SL.UEM.TOTL.ZS",       # Unemployment
        "SP.POP.TOTL",          # Population
        "SP.POP.GROW",          # Population growth
        "SP.URB.TOTL.IN.ZS",    # Urban population %
        "SP.DYN.LE00.IN",       # Life expectancy
        "GC.DOD.TOTL.GD.ZS",    # Central gov debt % GDP
        "FI.RES.TOTL.MO",       # Reserves in months of imports
    ]

    async def fetch(self) -> list[dict[str, Any]]:
        # Will use BigQuery public dataset bigquery-public-data.world_bank_wdi
        # via a SELECT into a staging table — no external HTTP needed.
        return []

    async def load(self, rows: list[dict[str, Any]]) -> int:
        return len(rows)

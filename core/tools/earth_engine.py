"""Earth Engine tool. Used by Population Agent for urban-extent + night-lights."""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class EarthEngineTool:
    """Pulls pre-computed indicators from BigQuery rather than calling EE in hot path."""

    async def night_lights_change(
        self, country_iso3: str, years: int = 5
    ) -> dict[str, float]:
        log.info("ee.night_lights_change", country=country_iso3, years=years)
        return {"pct_change": 0.0, "as_of_year": 0}

    async def urban_extent_change(
        self, country_iso3: str, years: int = 5
    ) -> dict[str, float]:
        log.info("ee.urban_extent_change", country=country_iso3, years=years)
        return {"pct_change": 0.0, "as_of_year": 0}

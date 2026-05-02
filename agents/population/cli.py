"""Run the Population Agent against one country, locally.

    python -m agents.population.cli COG
    python -m agents.population.cli NGA --horizon 60
    ATLASMIND_BQ_BACKEND=live python -m agents.population.cli KEN
"""

from __future__ import annotations

import argparse
import asyncio
import json
import uuid

from core.schemas import RunRequest, RunScope

from agents.population.agent import PopulationAgent


async def main(country: str, horizon: int, requested_by: str) -> None:
    request = RunRequest(
        run_id=str(uuid.uuid4()),
        scope=RunScope(country=country.upper(), horizon_months=horizon),
        depth="standard",
        requested_by=requested_by,
    )
    agent = PopulationAgent()
    result = await agent.run(request)
    print(json.dumps(result.model_dump(mode="json"), indent=2, default=str))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Run the AtlasMind Population Agent")
    ap.add_argument("country", help="ISO 3166-1 alpha-3 country code (e.g. COG)")
    ap.add_argument("--horizon", type=int, default=24)
    ap.add_argument("--requested-by", default="cli@atlasmind.local")
    args = ap.parse_args()
    asyncio.run(main(args.country, args.horizon, args.requested_by))

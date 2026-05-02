"""Strategy Conductor — orchestrates the 8 agents per run.

Execution plan (see docs/ARCHITECTURE.md §2):

    parallel:  Geopolitical, Market, Population, Technology Trend
    then:      Country Risk            (depends on Geopol + Market + Population)
    then:      Investment              (depends on Geopol + Market + Population + Country Risk + Tech Trend)
    then:      Scenario                (depends on all above)
    finally:   Strategy Briefing       (depends on everything)
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

import structlog

from core.memory import AgentMemory
from core.schemas import AgentResult, RunRequest

log = structlog.get_logger()


AgentInvoker = Callable[[RunRequest], Awaitable[AgentResult]]


@dataclass
class StrategyConductor:
    geopolitical: AgentInvoker
    market: AgentInvoker
    population: AgentInvoker
    technology_trend: AgentInvoker
    country_risk: AgentInvoker
    investment: AgentInvoker
    scenario: AgentInvoker
    strategy_briefing: AgentInvoker
    memory: AgentMemory = field(default_factory=AgentMemory.from_env)

    async def execute(self, request: RunRequest) -> dict[str, AgentResult]:
        log.info("conductor.start", run_id=request.run_id, scope=request.scope.model_dump())
        results: dict[str, AgentResult] = {}

        # Stage 1: independent foundations.
        stage1 = await asyncio.gather(
            self.geopolitical(request),
            self.market(request),
            self.population(request),
            self.technology_trend(request),
        )
        for r in stage1:
            results[r.agent] = r

        # Stage 2: country risk (composite of foundations).
        results["country_risk"] = await self.country_risk(request)

        # Stage 3: investment (uses everything we have so far).
        results["investment"] = await self.investment(request)

        # Stage 4: scenarios.
        results["scenario"] = await self.scenario(request)

        # Stage 5: briefing — produces the Doc + Slides + Sheet.
        results["strategy_briefing"] = await self.strategy_briefing(request)

        log.info(
            "conductor.complete",
            run_id=request.run_id,
            agents=list(results.keys()),
        )
        return results

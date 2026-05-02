"""Country Risk Agent. See docs/AGENTS.md §6."""

from __future__ import annotations

from core.runtime import AgentRunner
from core.schemas import AgentResult, RunRequest
from core.scoring import country_risk_score
from core.tools import BigQueryTool, GeminiClient


class CountryRiskAgent(AgentRunner):
    name = "country_risk"

    def __init__(self) -> None:
        super().__init__()
        self.bq = BigQueryTool()
        self.llm = GeminiClient.from_env()

    async def run(self, request: RunRequest) -> AgentResult:
        # Will load upstream agents' results from memory and compute the composite.
        return AgentResult(
            run_id=request.run_id,
            agent=self.name,
            as_of=self.now(),
            claims=[],
            scores={
                "country_risk": country_risk_score({}),
                "infrastructure_gap": 0.0,
                "strategic_importance": 0.0,
            },
            notes="stub",
        )

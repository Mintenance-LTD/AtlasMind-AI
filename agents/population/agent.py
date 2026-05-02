"""Population Agent. See docs/AGENTS.md §4."""

from __future__ import annotations

from core.runtime import AgentRunner
from core.schemas import AgentResult, RunRequest
from core.tools import BigQueryTool, EarthEngineTool, GeminiClient


class PopulationAgent(AgentRunner):
    name = "population"

    def __init__(self) -> None:
        super().__init__()
        self.bq = BigQueryTool()
        self.ee = EarthEngineTool()
        self.llm = GeminiClient.from_env()

    async def run(self, request: RunRequest) -> AgentResult:
        return AgentResult(
            run_id=request.run_id,
            agent=self.name,
            as_of=self.now(),
            claims=[],
            scores={"demographic_growth": 0.0},
            notes="stub",
        )

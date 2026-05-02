"""Market Agent. See docs/AGENTS.md §2."""

from __future__ import annotations

from core.runtime import AgentRunner
from core.schemas import AgentResult, RunRequest
from core.tools import BigQueryTool, GeminiClient, VertexSearchTool


class MarketAgent(AgentRunner):
    name = "market"

    def __init__(self) -> None:
        super().__init__()
        self.bq = BigQueryTool()
        self.search = VertexSearchTool.from_env()
        self.llm = GeminiClient.from_env()

    async def run(self, request: RunRequest) -> AgentResult:
        return AgentResult(
            run_id=request.run_id,
            agent=self.name,
            as_of=self.now(),
            claims=[],
            scores={"market_opportunity": 0.0},
            notes="stub",
        )

"""Geopolitical Agent. See docs/AGENTS.md §1."""

from __future__ import annotations

from core.runtime import AgentRunner
from core.schemas import AgentResult, RunRequest
from core.scoring import political_risk_score
from core.tools import BigQueryTool, GeminiClient, VertexSearchTool

from agents.geopolitical.prompts import SYSTEM_PROMPT


class GeopoliticalAgent(AgentRunner):
    name = "geopolitical"

    def __init__(self) -> None:
        super().__init__()
        self.bq = BigQueryTool()
        self.search = VertexSearchTool.from_env()
        self.llm = GeminiClient.from_env()

    async def run(self, request: RunRequest) -> AgentResult:
        # Phase-1 stub. Real implementation will:
        # 1. Pull WGI, ACLED, election calendar from BigQuery for request.scope.country
        # 2. Pull recent news / IMF Article IV via VertexSearch + grounded Google Search
        # 3. Ask Gemini Pro (with SYSTEM_PROMPT) to synthesise claims
        # 4. Validate citations, compute political_risk score, return AgentResult
        return AgentResult(
            run_id=request.run_id,
            agent=self.name,
            as_of=self.now(),
            claims=[],
            scores={"political_risk": political_risk_score({})},
            notes="stub",
        )

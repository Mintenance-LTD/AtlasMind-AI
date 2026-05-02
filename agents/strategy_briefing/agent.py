"""Strategy Briefing Agent. See docs/AGENTS.md §8."""

from __future__ import annotations

from core.runtime import AgentRunner
from core.schemas import AgentResult, RunRequest
from core.tools import GeminiClient, WorkspaceDocsTool


class StrategyBriefingAgent(AgentRunner):
    name = "strategy_briefing"

    def __init__(self) -> None:
        super().__init__()
        self.docs = WorkspaceDocsTool.from_env()
        self.llm = GeminiClient.from_env()

    async def run(self, request: RunRequest) -> AgentResult:
        # Will load all upstream agent outputs via memory.load_run_context(),
        # then call WorkspaceDocsTool to render brief / deck / scorecard.
        return AgentResult(
            run_id=request.run_id,
            agent=self.name,
            as_of=self.now(),
            claims=[],
            scores={},
            notes="stub",
        )

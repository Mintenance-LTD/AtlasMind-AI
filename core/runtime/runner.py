"""Common runtime for every agent: HTTP entrypoint, tracing, retries, memory."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from datetime import UTC, datetime

import structlog
from fastapi import FastAPI, HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential

from core.memory import AgentMemory
from core.schemas import AgentResult, RunRequest
from core.tools.citations import validate_claims

log = structlog.get_logger()


class AgentRunner(ABC):
    """Subclass this for each agent. Implement `run()`."""

    name: str = "agent"

    def __init__(self, memory: AgentMemory | None = None) -> None:
        self.memory = memory or AgentMemory.from_env()

    @abstractmethod
    async def run(self, request: RunRequest) -> AgentResult:
        """Produce an AgentResult for the given run request."""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def _execute(self, request: RunRequest) -> AgentResult:
        log.info("agent.run.start", agent=self.name, run_id=request.run_id)
        result = await self.run(request)
        validate_claims(result.claims)
        await self.memory.persist_result(result)
        log.info(
            "agent.run.complete",
            agent=self.name,
            run_id=request.run_id,
            claim_count=len(result.claims),
            scores=result.scores,
        )
        return result

    def now(self) -> datetime:
        return datetime.now(UTC)


def agent_app(runner: AgentRunner) -> FastAPI:
    """Wrap an AgentRunner as a Cloud Run-ready FastAPI app."""

    app = FastAPI(title=f"atlasmind-{runner.name}")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok", "agent": runner.name}

    @app.post("/run", response_model=AgentResult)
    async def run(request: RunRequest) -> AgentResult:
        try:
            return await runner._execute(request)
        except Exception as exc:
            log.error("agent.run.failed", agent=runner.name, error=str(exc))
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "agent": runner.name,
            "env": os.environ.get("ATLASMIND_ENV", "dev"),
            "version": "0.1.0",
        }

    return app

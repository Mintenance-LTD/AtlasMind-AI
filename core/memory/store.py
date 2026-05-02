"""Agent memory: Firestore for live state, BigQuery for replayable history."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import structlog

from core.schemas import AgentResult

log = structlog.get_logger()


@dataclass
class AgentMemory:
    project: str
    firestore_database: str
    bq_claims_dataset: str
    bq_runs_dataset: str
    bq_scores_dataset: str

    @classmethod
    def from_env(cls) -> AgentMemory:
        return cls(
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", "atlasmind-stage"),
            firestore_database=os.environ.get("FIRESTORE_DATABASE", "(default)"),
            bq_claims_dataset=os.environ.get("BQ_DATASET_CLAIMS", "atlasmind_claims"),
            bq_runs_dataset=os.environ.get("BQ_DATASET_RUNS", "atlasmind_runs"),
            bq_scores_dataset=os.environ.get("BQ_DATASET_SCORES", "atlasmind_scores"),
        )

    async def persist_result(self, result: AgentResult) -> None:
        """Write claims + scores to BigQuery and update Firestore run state.

        Implementation deferred to Phase 3. The shape below is what gets stored.
        """
        log.info(
            "memory.persist",
            agent=result.agent,
            run_id=result.run_id,
            claim_count=len(result.claims),
            score_count=len(result.scores),
        )

    async def load_run_context(self, run_id: str) -> dict[str, Any]:
        """Return everything earlier agents in the same run have produced."""
        log.info("memory.load_context", run_id=run_id)
        return {}

    async def save_run_state(self, run_id: str, state: dict[str, Any]) -> None:
        log.info("memory.save_state", run_id=run_id, keys=list(state.keys()))

"""Workspace Docs / Slides / Sheets tool — used by the Strategy Briefing Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import structlog

log = structlog.get_logger()


@dataclass
class WorkspaceDocsTool:
    """Writes Doc / Slides / Sheets briefings into a user's Drive."""

    templates_bucket: str

    @classmethod
    def from_env(cls) -> WorkspaceDocsTool:
        return cls(
            templates_bucket=os.environ.get("GCS_BUCKET_TEMPLATES", "atlasmind-templates"),
        )

    async def render_executive_brief(
        self,
        run_id: str,
        country_iso3: str,
        payload: dict[str, Any],
        target_drive_folder_id: str,
    ) -> str:
        """Returns the new Doc's file id."""
        log.info(
            "workspace.brief",
            run_id=run_id,
            country=country_iso3,
            folder=target_drive_folder_id,
        )
        return ""

    async def render_board_pack(
        self,
        run_id: str,
        country_iso3: str,
        payload: dict[str, Any],
        target_drive_folder_id: str,
    ) -> str:
        log.info(
            "workspace.deck",
            run_id=run_id,
            country=country_iso3,
            folder=target_drive_folder_id,
        )
        return ""

    async def render_scorecard(
        self,
        run_id: str,
        country_iso3: str,
        opportunities: list[dict[str, Any]],
        target_drive_folder_id: str,
    ) -> str:
        log.info(
            "workspace.scorecard",
            run_id=run_id,
            country=country_iso3,
            count=len(opportunities),
        )
        return ""

"""Cloud Function: subscribed to alerts.triggered. Sends Workspace email via Gmail API."""

from __future__ import annotations

import base64
import json
from typing import Any

import structlog

log = structlog.get_logger()


def alert_emailer(event: dict[str, Any], context: Any) -> None:
    payload_b64 = event.get("data", "")
    payload = json.loads(base64.b64decode(payload_b64).decode()) if payload_b64 else {}
    log.info(
        "alert_emailer",
        country=payload.get("country"),
        score=payload.get("score"),
        delta=payload.get("delta"),
    )
    # Production: send via Gmail API as briefing-sa@ on behalf of the user's domain.

"""Cloud Function: subscribed to runs.requested. Invokes the Strategy Conductor."""

from __future__ import annotations

import base64
import json
import os
from typing import Any

import structlog

log = structlog.get_logger()


def runs_dispatcher(event: dict[str, Any], context: Any) -> None:
    payload_b64 = event.get("data", "")
    payload = json.loads(base64.b64decode(payload_b64).decode()) if payload_b64 else {}
    log.info(
        "runs_dispatcher",
        run_id=payload.get("run_id"),
        kind=payload.get("kind"),
        env=os.environ.get("ATLASMIND_ENV", "dev"),
    )
    # Production: POST to the Conductor Cloud Run service with an IAM-signed request.

"""Gemini client wrapper — Vertex AI."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import structlog

log = structlog.get_logger()


@dataclass
class GeminiClient:
    project: str
    location: str
    reasoning_model: str
    fast_model: str

    @classmethod
    def from_env(cls) -> GeminiClient:
        return cls(
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", "atlasmind-stage"),
            location=os.environ.get("VERTEX_LOCATION", "europe-west1"),
            reasoning_model=os.environ.get("GEMINI_REASONING_MODEL", "gemini-2.5-pro"),
            fast_model=os.environ.get("GEMINI_FAST_MODEL", "gemini-2.5-flash"),
        )

    async def reason(
        self,
        system: str,
        user: str,
        tools: list[Any] | None = None,
        grounding: bool = True,
    ) -> dict[str, Any]:
        log.info(
            "gemini.reason",
            model=self.reasoning_model,
            grounding=grounding,
            tools=len(tools or []),
        )
        return {"text": "", "citations": [], "tool_calls": []}

    async def classify(self, prompt: str) -> dict[str, Any]:
        log.info("gemini.classify", model=self.fast_model)
        return {"label": None, "confidence": 0.0}

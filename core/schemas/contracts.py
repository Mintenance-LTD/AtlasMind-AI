"""I/O contracts shared by every agent. See docs/TECH_PACK.md §7."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Evidence(BaseModel):
    source: str
    url: HttpUrl | None = None
    as_of: datetime
    excerpt: str | None = None


class Claim(BaseModel):
    statement: str
    confidence: Confidence
    evidence: list[Evidence] = Field(min_length=1)
    early_warning: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class Scenario(BaseModel):
    name: Literal["base", "upside", "stress"] | str
    probability: float = Field(ge=0.0, le=1.0)
    narrative: str
    drivers: list[str]
    triggers: list[str]


class RunScope(BaseModel):
    country: str | None = Field(default=None, description="ISO 3166-1 alpha-3")
    region: str | None = None
    sector: str | None = None
    theme: str | None = None
    horizon_months: int = Field(default=24, ge=1, le=120)


class RunRequest(BaseModel):
    run_id: str
    scope: RunScope
    depth: Literal["standard", "deep"] = "standard"
    requested_by: str


class AgentResult(BaseModel):
    run_id: str
    agent: str
    as_of: datetime
    claims: list[Claim]
    scores: dict[str, float] = Field(default_factory=dict)
    raw_signals_uri: str | None = None
    notes: str | None = None

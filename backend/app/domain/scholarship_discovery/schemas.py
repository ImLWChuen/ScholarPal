"""
Scholarship Discovery Domain Module.
Covers scholarship listing, search, filtering, and freshness tracking.
Non-negotiable rule 4: Failed retrieval keeps the last known record and flags uncertain freshness;
it never marks a scholarship closed.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class FreshnessStatus(str, Enum):
    FRESH = "fresh"
    UNCERTAIN = "uncertain"  # flagged when retrieval failed; record preserved


class ScholarshipStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    UPCOMING = "upcoming"


class ScholarshipBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    provider: str
    official_portal_url: str
    deadline: datetime | None = None
    status: ScholarshipStatus = ScholarshipStatus.OPEN
    freshness: FreshnessStatus = FreshnessStatus.FRESH
    last_verified_at: datetime | None = None

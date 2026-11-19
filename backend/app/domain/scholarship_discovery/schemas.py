"""
Scholarship Discovery Domain Module.
Covers scholarship listing, search, filtering, and freshness tracking.
Non-negotiable rule 4: Failed retrieval keeps the last known record and flags uncertain freshness;
it never marks a scholarship closed.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.domain.shared_enums import (
    FreshnessStatus,
    RetrievalStatus,
    ScholarshipStatus,
    VersionStatus,
)


# ---------------------------------------------------------------------------
# Source Schemas
# ---------------------------------------------------------------------------
class SourceBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255)
    base_url: str
    config: dict[str, Any] = Field(default_factory=dict)
    schedule: str = "0 0 * * *"
    is_active: bool = True


class SourceCreate(SourceBase):
    id: str | None = None


class SourceUpdate(BaseModel):
    name: str | None = None
    base_url: str | None = None
    config: dict[str, Any] | None = None
    schedule: str | None = None
    is_active: bool | None = None


class SourceRead(SourceBase):
    id: str
    last_retrieved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Retrieval & Claim Schemas
# ---------------------------------------------------------------------------
class RetrievalBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_id: str
    url: str
    status: RetrievalStatus = RetrievalStatus.PENDING
    http_status_code: int | None = None
    error: str | None = None
    content_hash: str | None = Field(default=None, max_length=64)


class RetrievalCreate(RetrievalBase):
    id: str | None = None


class RetrievalRead(RetrievalBase):
    id: str
    retrieved_at: datetime


class RetrievalProcessingClaimBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_id: str
    url: str
    content_hash: str = Field(..., max_length=64)


class RetrievalProcessingClaimCreate(RetrievalProcessingClaimBase):
    id: str | None = None


class RetrievalProcessingClaimRead(RetrievalProcessingClaimBase):
    id: str
    claimed_at: datetime
    processed_at: datetime | None = None


# ---------------------------------------------------------------------------
# Scholarship Schemas
# ---------------------------------------------------------------------------
class ScholarshipBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., min_length=1)
    provider: str = Field(..., min_length=1)
    official_portal_url: str
    deadline: datetime | None = None
    status: ScholarshipStatus = ScholarshipStatus.OPEN
    freshness: FreshnessStatus = FreshnessStatus.FRESH
    last_verified_at: datetime | None = None


class ScholarshipCreate(ScholarshipBase):
    id: str | None = None
    source_id: str | None = None


class ScholarshipUpdate(BaseModel):
    title: str | None = None
    provider: str | None = None
    official_portal_url: str | None = None
    deadline: datetime | None = None
    status: ScholarshipStatus | None = None
    freshness: FreshnessStatus | None = None
    last_verified_at: datetime | None = None


class ScholarshipRead(ScholarshipBase):
    id: str
    source_id: str | None = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Scholarship Version Schemas
# ---------------------------------------------------------------------------
class ScholarshipVersionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scholarship_id: str
    application_cycle: str
    version_number: int = 1
    title: str
    description: str | None = None
    coverage_details: dict[str, Any] | None = None
    deadline: datetime | None = None
    status: VersionStatus = VersionStatus.DRAFT
    raw_extracted_data: dict[str, Any] | None = None


class ScholarshipVersionCreate(ScholarshipVersionBase):
    id: str | None = None
    retrieval_id: str | None = None


class ScholarshipVersionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    coverage_details: dict[str, Any] | None = None
    deadline: datetime | None = None
    status: VersionStatus | None = None
    raw_extracted_data: dict[str, Any] | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None


class ScholarshipVersionRead(ScholarshipVersionBase):
    id: str
    retrieval_id: str | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Filter Query Schema
# ---------------------------------------------------------------------------
class ScholarshipFilter(BaseModel):
    query: str | None = None
    provider: str | None = None
    study_level: str | None = None
    status: ScholarshipStatus | None = None
    freshness: FreshnessStatus | None = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

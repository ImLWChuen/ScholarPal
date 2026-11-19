"""
Extraction and Evidence Review Domain Module.
Covers LLM structured extraction, Jev evidence verification, and admin review console.
Non-negotiable rule 3: Jev results assist the administrator and never auto-publish.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.domain.shared_enums import EvidenceLabel


class ReviewStatus(str, Enum):
    PENDING_REVIEW = "pending_review"  # Never auto-published
    APPROVED = "approved"  # Explicit admin action
    REJECTED = "rejected"  # Explicit admin action


# ---------------------------------------------------------------------------
# Required Document Schemas
# ---------------------------------------------------------------------------
class RequiredDocumentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scholarship_version_id: str
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    is_mandatory: bool = True
    format_instructions: str | None = None


class RequiredDocumentCreate(RequiredDocumentBase):
    id: str | None = None


class RequiredDocumentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_mandatory: bool | None = None
    format_instructions: str | None = None


class RequiredDocumentRead(RequiredDocumentBase):
    id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Evidence Check (Jev) Schemas
# ---------------------------------------------------------------------------
class EvidenceCheckBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scholarship_version_id: str
    requirement_id: str | None = None
    retrieval_id: str | None = None
    jev_label: EvidenceLabel
    probabilities: dict[str, float] = Field(default_factory=dict)
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence_excerpt: str | None = None
    admin_verdict: str | None = None
    admin_notes: str | None = None


class EvidenceCheckCreate(EvidenceCheckBase):
    id: str | None = None


class EvidenceCheckUpdate(BaseModel):
    jev_label: EvidenceLabel | None = None
    probabilities: dict[str, float] | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    evidence_excerpt: str | None = None
    admin_verdict: str | None = None
    admin_notes: str | None = None


class EvidenceCheckRead(EvidenceCheckBase):
    id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Extraction Review Schemas (Legacy compatibility)
# ---------------------------------------------------------------------------
class ExtractionReviewBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scholarship_id: str
    source_url: str
    extracted_data: dict[str, Any]
    jev_evidence_score: float | None = None
    jev_evidence_verdict: str | None = None
    review_status: ReviewStatus = ReviewStatus.PENDING_REVIEW
    admin_notes: str | None = None
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None


class ExtractionReviewCreate(ExtractionReviewBase):
    id: str | None = None


class ExtractionReviewUpdate(BaseModel):
    extracted_data: dict[str, Any] | None = None
    jev_evidence_score: float | None = None
    jev_evidence_verdict: str | None = None
    review_status: ReviewStatus | None = None
    admin_notes: str | None = None
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None


class ExtractionReviewRead(ExtractionReviewBase):
    id: str

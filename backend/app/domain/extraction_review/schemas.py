"""
Extraction and Evidence Review Domain Module.
Covers LLM structured extraction, Jev evidence verification, and admin review console.
Non-negotiable rule 3: Jev results assist the administrator and never auto-publish.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class ReviewStatus(str, Enum):
    PENDING_REVIEW = "pending_review"  # Never auto-published
    APPROVED = "approved"  # Explicit admin action
    REJECTED = "rejected"  # Explicit admin action


class ExtractionReviewBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scholarship_id: str
    source_url: str
    extracted_data: dict[str, Any]
    jev_evidence_score: float | None = None
    jev_evidence_verdict: str | None = None  # Choice primitive result
    review_status: ReviewStatus = ReviewStatus.PENDING_REVIEW
    admin_notes: str | None = None
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None

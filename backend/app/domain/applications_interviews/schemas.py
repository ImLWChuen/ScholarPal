"""
Applications and Interviews Domain Module.
Covers student application tracking, interview milestones, checklist, and deadlines.
Non-negotiable rule 7: Students submit on official provider portals;
ScholarPal never marks submission automatically (requires explicit student action/confirmation).
Non-negotiable rule 8: Backend enforces record ownership on every student endpoint.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.shared_enums import ApplicationStage


# ---------------------------------------------------------------------------
# Application Schemas
# ---------------------------------------------------------------------------
class ApplicationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: str
    scholarship_id: str
    stage: ApplicationStage = ApplicationStage.SAVED
    submitted_at: datetime | None = None
    submission_reference: str | None = None
    portal_submission_reference: str | None = None  # Legacy alias
    notes: str | None = None


class ApplicationCreate(ApplicationBase):
    id: str | None = None


class ApplicationUpdate(BaseModel):
    stage: ApplicationStage | None = None
    submitted_at: datetime | None = None
    submission_reference: str | None = None
    portal_submission_reference: str | None = None
    notes: str | None = None


class ApplicationRead(ApplicationBase):
    id: str
    created_at: datetime
    updated_at: datetime


# Backward compatibility alias
StudentApplicationBase = ApplicationBase


# ---------------------------------------------------------------------------
# Application Task Schemas
# ---------------------------------------------------------------------------
class ApplicationTaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    application_id: str
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    task_key: str | None = None
    is_completed: bool = False
    due_date: datetime | None = None


class ApplicationTaskCreate(ApplicationTaskBase):
    id: str | None = None


class ApplicationTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    task_key: str | None = None
    is_completed: bool | None = None
    due_date: datetime | None = None


class ApplicationTaskRead(ApplicationTaskBase):
    id: str
    completed_at: datetime | None = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Document Checklist Item Schemas
# ---------------------------------------------------------------------------
class DocumentChecklistItemBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    application_id: str
    required_document_id: str
    file_path: str | None = None
    file_name: str | None = None
    is_verified: bool = False
    notes: str | None = None


class DocumentChecklistItemCreate(DocumentChecklistItemBase):
    id: str | None = None


class DocumentChecklistItemUpdate(BaseModel):
    file_path: str | None = None
    file_name: str | None = None
    is_verified: bool | None = None
    uploaded_at: datetime | None = None
    notes: str | None = None


class DocumentChecklistItemRead(DocumentChecklistItemBase):
    id: str
    uploaded_at: datetime | None = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Interview Schemas
# ---------------------------------------------------------------------------
class InterviewBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    application_id: str
    scheduled_at: datetime
    location_or_link: str | None = None
    round_name: str = "First Round"
    status: str = "scheduled"  # scheduled, completed, cancelled, rescheduled
    prep_notes: str | None = None
    feedback: str | None = None


class InterviewCreate(InterviewBase):
    id: str | None = None


class InterviewUpdate(BaseModel):
    scheduled_at: datetime | None = None
    location_or_link: str | None = None
    round_name: str | None = None
    status: str | None = None
    prep_notes: str | None = None
    feedback: str | None = None


class InterviewRead(InterviewBase):
    id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Award Offer Schemas
# ---------------------------------------------------------------------------
class AwardOfferBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    application_id: str
    offer_amount: float | None = Field(default=None, ge=0.0)
    currency: str = "MYR"
    bond_duration_years: int | None = Field(default=None, ge=0)
    decision: str = "pending"  # pending, accepted, declined
    decision_deadline: datetime | None = None
    terms_summary: str | None = None


class AwardOfferCreate(AwardOfferBase):
    id: str | None = None


class AwardOfferUpdate(BaseModel):
    offer_amount: float | None = Field(default=None, ge=0.0)
    currency: str | None = None
    bond_duration_years: int | None = Field(default=None, ge=0)
    decision: str | None = None
    decision_deadline: datetime | None = None
    terms_summary: str | None = None


class AwardOfferRead(AwardOfferBase):
    id: str
    received_at: datetime
    decided_at: datetime | None = None
    created_at: datetime

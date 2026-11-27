"""
Applications and Interviews Domain Module.
Covers student application tracking, interview milestones, checklist, and deadlines.
Non-negotiable rule 7: Students submit on official provider portals;
ScholarPal never marks submission automatically (requires explicit student action/confirmation).
Non-negotiable rule 8: Backend enforces record ownership on every student endpoint.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.common_validators import reject_explicit_nulls
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

    @model_validator(mode="after")
    def validate_non_nullable_fields(self) -> ApplicationUpdate:
        return reject_explicit_nulls(self, ("stage",))


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

    @model_validator(mode="after")
    def validate_non_nullable_fields(self) -> ApplicationTaskUpdate:
        return reject_explicit_nulls(self, ("title", "task_key", "is_completed"))


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
    is_ready: bool = False
    notes: str | None = None


class DocumentChecklistItemCreate(DocumentChecklistItemBase):
    id: str | None = None


class DocumentChecklistItemCreateRequest(BaseModel):
    """Request schema for creating a checklist item under an application."""

    id: str | None = None
    required_document_id: str
    file_path: str | None = None
    file_name: str | None = None
    is_ready: bool = False
    notes: str | None = None


class DocumentChecklistItemUpdate(BaseModel):
    file_path: str | None = None
    file_name: str | None = None
    is_ready: bool | None = None
    uploaded_at: datetime | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_non_nullable_fields(self) -> DocumentChecklistItemUpdate:
        return reject_explicit_nulls(self, ("is_ready",))


class DocumentChecklistItemRead(DocumentChecklistItemBase):
    id: str
    uploaded_at: datetime | None = None
    created_at: datetime


class DocumentReadinessRead(BaseModel):
    """Document readiness calculation result for an application."""

    ready_count: int
    total_required: int | None
    readiness_percentage: float | None
    status: str
    display: str


class ApplicationChecklistRead(BaseModel):
    """Checklist items and computed document readiness for a saved application."""

    application_id: str
    readiness: DocumentReadinessRead
    items: list[DocumentChecklistItemRead]


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
    feedback: str | None = None


class InterviewCreate(InterviewBase):
    id: str | None = None


class InterviewUpdate(BaseModel):
    scheduled_at: datetime | None = None
    location_or_link: str | None = None
    round_name: str | None = None
    status: str | None = None
    feedback: str | None = None

    @model_validator(mode="after")
    def validate_non_nullable_fields(self) -> InterviewUpdate:
        return reject_explicit_nulls(self, ("scheduled_at", "round_name", "status"))


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


class AwardOfferCreate(AwardOfferBase):
    id: str | None = None


class AwardOfferUpdate(BaseModel):
    offer_amount: float | None = Field(default=None, ge=0.0)
    currency: str | None = None
    bond_duration_years: int | None = Field(default=None, ge=0)
    decision: str | None = None
    decision_deadline: datetime | None = None

    @model_validator(mode="after")
    def validate_non_nullable_fields(self) -> AwardOfferUpdate:
        return reject_explicit_nulls(self, ("currency", "decision"))


class AwardOfferRead(AwardOfferBase):
    id: str
    received_at: datetime
    decided_at: datetime | None = None
    created_at: datetime

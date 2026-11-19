"""
SQLAlchemy models for Applications and Interviews domain.
Rule 7: Never marked submitted automatically.
Rule 8: student_id index for strict ownership enforcement.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    event,
    func,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from app.core.db import Base

if TYPE_CHECKING:
    from app.domain.extraction_review.models import RequiredDocument
    from app.domain.profile_preparation.models import User
    from app.domain.scholarship_discovery.models import Scholarship


class ApplicationStage(str, Enum):
    SAVED = "Saved"
    PREPARING = "Preparing"
    SUBMITTED = "Submitted"
    INTERVIEW = "Interview"
    OFFERED = "Offered"
    UNSUCCESSFUL = "Unsuccessful"
    WITHDRAWN = "Withdrawn"


class Application(Base):
    """
    Student application record tracking progress through the scholarship pipeline.
    Rule 7: Students submit on official provider portals; ScholarPal never auto-submits.
    Rule 8: Strict record ownership via student_id.
    """

    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    student_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    scholarship_id: Mapped[str] = mapped_column(
        String, ForeignKey("scholarships.id", ondelete="CASCADE"), index=True, nullable=False
    )
    stage: Mapped[str] = mapped_column(
        String, default=ApplicationStage.SAVED.value, nullable=False, index=True
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submission_reference: Mapped[str | None] = mapped_column(String, nullable=True)
    # Synonym for backwards-compatibility with legacy portal_submission_reference
    portal_submission_reference = synonym("submission_reference")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    student: Mapped[User] = relationship("User", foreign_keys=[student_id])
    scholarship: Mapped[Scholarship] = relationship("Scholarship", foreign_keys=[scholarship_id])
    tasks: Mapped[list[ApplicationTask]] = relationship(
        "ApplicationTask", back_populates="application", cascade="all, delete-orphan"
    )
    document_checklist: Mapped[list[DocumentChecklistItem]] = relationship(
        "DocumentChecklistItem", back_populates="application", cascade="all, delete-orphan"
    )
    interviews: Mapped[list[Interview]] = relationship(
        "Interview", back_populates="application", cascade="all, delete-orphan"
    )
    award_offer: Mapped[AwardOffer | None] = relationship(
        "AwardOffer", back_populates="application", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "uq_applications_active_student_scholarship",
            "student_id",
            "scholarship_id",
            unique=True,
            postgresql_where=(stage != ApplicationStage.WITHDRAWN.value),
            sqlite_where=(stage != ApplicationStage.WITHDRAWN.value),
        ),
    )


# Alias for backward-compatibility with earlier prototype
StudentApplication = Application


class ApplicationTask(Base):
    """
    Task item associated with preparing an application.
    Uniqueness constraint on (application_id, task_key) prevents duplicate task generation.
    """

    __tablename__ = "application_tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    application_id: Mapped[str] = mapped_column(
        String, ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_key: Mapped[str] = mapped_column(String, nullable=False, index=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    application: Mapped[Application] = relationship("Application", back_populates="tasks")

    __table_args__ = (
        UniqueConstraint("application_id", "task_key", name="uq_application_tasks_app_key"),
    )


class DocumentChecklistItem(Base):
    """
    Tracks upload and verification of required documents for an application.
    Uniqueness constraint on (application_id, required_document_id) prevents duplicate entries.
    """

    __tablename__ = "document_checklist_items"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    application_id: Mapped[str] = mapped_column(
        String, ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False
    )
    required_document_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("required_documents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    file_path: Mapped[str | None] = mapped_column(String, nullable=True)
    file_name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    application: Mapped[Application] = relationship(
        "Application", back_populates="document_checklist"
    )
    required_document: Mapped[RequiredDocument] = relationship("RequiredDocument")

    __table_args__ = (
        UniqueConstraint(
            "application_id",
            "required_document_id",
            name="uq_doc_checklist_app_doc",
        ),
    )


@event.listens_for(DocumentChecklistItem, "before_insert")
@event.listens_for(DocumentChecklistItem, "before_update")
def validate_document_checklist_item_slot(
    mapper: Any, connection: Any, target: DocumentChecklistItem
) -> None:
    """
    Enforces that a checklist slot only references a required document
    belonging to the application's associated scholarship.
    """
    from app.domain.extraction_review.models import RequiredDocument
    from app.domain.scholarship_discovery.models import ScholarshipVersion

    stmt = (
        select(Application.scholarship_id, ScholarshipVersion.scholarship_id)
        .select_from(Application)
        .join(RequiredDocument, RequiredDocument.id == target.required_document_id)
        .join(ScholarshipVersion, ScholarshipVersion.id == RequiredDocument.scholarship_version_id)
        .where(Application.id == target.application_id)
    )
    row = connection.execute(stmt).first()
    if row and row[0] != row[1]:
        raise ValueError(
            f"Slot integrity violation: Required document '{target.required_document_id}' "
            f"belongs to scholarship '{row[1]}', not application scholarship '{row[0]}'."
        )


class Interview(Base):
    """Scholarship interview rounds and assessment sessions."""

    __tablename__ = "interviews"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    application_id: Mapped[str] = mapped_column(
        String, ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False
    )
    round_name: Mapped[str] = mapped_column(String, default="First Round", nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    location_or_url: Mapped[str | None] = mapped_column(String, nullable=True)
    format: Mapped[str] = mapped_column(String, default="in-person", nullable=False)
    status: Mapped[str] = mapped_column(String, default="scheduled", nullable=False, index=True)
    feedback_or_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    application: Mapped[Application] = relationship("Application", back_populates="interviews")


class AwardOffer(Base):
    """Scholarship award offer terms, funding, and bond commitment."""

    __tablename__ = "award_offers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    application_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("applications.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    offer_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="MYR", nullable=False)
    coverage_terms: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    bond_duration_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Decision e.g. "pending", "accepted", "declined"
    decision: Mapped[str] = mapped_column(String, default="pending", nullable=False, index=True)
    decision_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    application: Mapped[Application] = relationship("Application", back_populates="award_offer")

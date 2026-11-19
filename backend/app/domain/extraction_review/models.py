"""
SQLAlchemy models for Extraction and Evidence Review domain.
Rule 3: Jev results assist the administrator and never auto-publish.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.domain.eligibility_impact.models import Requirement
    from app.domain.scholarship_discovery.models import ScholarshipVersion


class RequiredDocument(Base):
    """Document specified as required by a scholarship version."""

    __tablename__ = "required_documents"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    scholarship_version_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("scholarship_versions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    format_instructions: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    scholarship_version: Mapped[ScholarshipVersion] = relationship(
        "ScholarshipVersion", back_populates="required_documents"
    )


class EvidenceCheck(Base):
    """
    Jev by TypeSafe AI evidence verification record for an extracted requirement.
    Rule 3: Jev results assist the administrator and never auto-publish.
    Version-requirement pair constraint guarantees requirement belongs to the same version.
    """

    __tablename__ = "evidence_checks"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    scholarship_version_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("scholarship_versions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    requirement_id: Mapped[str | None] = mapped_column(
        String,
        index=True,
        nullable=True,
    )
    retrieval_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("retrievals.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    jev_label: Mapped[str] = mapped_column(String, nullable=False)
    probabilities: Mapped[dict[str, float]] = mapped_column(JSON, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    admin_verdict: Mapped[str | None] = mapped_column(String, nullable=True)
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    scholarship_version: Mapped[ScholarshipVersion] = relationship(
        "ScholarshipVersion",
        back_populates="evidence_checks",
        overlaps="evidence_checks,requirement",
    )
    requirement: Mapped[Requirement | None] = relationship(
        "Requirement",
        back_populates="evidence_checks",
        foreign_keys=[scholarship_version_id, requirement_id],
        overlaps="evidence_checks,scholarship_version",
    )

    __table_args__ = (
        UniqueConstraint(
            "scholarship_version_id",
            "requirement_id",
            name="uq_evidence_checks_version_req",
        ),
        ForeignKeyConstraint(
            ["scholarship_version_id", "requirement_id"],
            ["requirements.scholarship_version_id", "requirements.id"],
            ondelete="CASCADE",
            name="fk_evidence_checks_version_requirement",
        ),
    )


class ExtractionReview(Base):
    """Legacy compatibility model for prototype extraction review records."""

    __tablename__ = "extraction_reviews"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    scholarship_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    source_url: Mapped[str] = mapped_column(String, nullable=False)
    extracted_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    jev_evidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    jev_evidence_verdict: Mapped[str | None] = mapped_column(String, nullable=True)
    review_status: Mapped[str] = mapped_column(String, default="pending_review", nullable=False)
    admin_notes: Mapped[str | None] = mapped_column(String, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String, nullable=True)

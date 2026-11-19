"""
SQLAlchemy models for Eligibility and Change Impact domain.
Rule 1: Predefined rules stored deterministically.
Rule 2: Requirements evaluated as satisfied, unmet, or unresolved.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.domain.extraction_review.models import EvidenceCheck
    from app.domain.scholarship_discovery.models import ScholarshipVersion


class Requirement(Base):
    """
    Deterministic requirement rule extracted and associated with a scholarship version.
    Rule 1 & Rule 2: Deterministic evaluation without LLM.
    """

    __tablename__ = "requirements"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    scholarship_version_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("scholarship_versions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    # Type e.g. "academic_cgpa", "nationality", "study_level", "household_income", "field_of_study"
    type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # Operator e.g. "eq", "gte", "lte", "in", "contains"
    operator: Mapped[str] = mapped_column(String, nullable=False)
    # Value e.g. 3.75, "Malaysian", ["Engineering"]
    value: Mapped[Any] = mapped_column(JSON, nullable=False)
    # Mandatory flag: if unmet -> "Does not meet recorded requirements"
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    # Source excerpt: verbatim evidence from official portal
    source_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Subjective flag: e.g. leadership potential, extracurricular essay
    is_subjective: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    scholarship_version: Mapped[ScholarshipVersion] = relationship(
        "ScholarshipVersion", back_populates="requirements"
    )
    evidence_checks: Mapped[list[EvidenceCheck]] = relationship(
        "EvidenceCheck", back_populates="requirement", cascade="all, delete-orphan"
    )


class EligibilityRule(Base):
    """Legacy compatibility model for existing prototype rules."""

    __tablename__ = "eligibility_rules"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    scholarship_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    criterion_code: Mapped[str] = mapped_column(String, nullable=False)
    rule_type: Mapped[str] = mapped_column(String, nullable=False)
    rule_parameters: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

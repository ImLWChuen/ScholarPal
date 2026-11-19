"""
SQLAlchemy models for Scholarship Discovery domain.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.domain.eligibility_impact.models import Requirement
    from app.domain.extraction_review.models import EvidenceCheck, RequiredDocument


class VersionStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    base_url: Mapped[str] = mapped_column(String, nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    schedule: Mapped[str] = mapped_column(String, default="0 0 * * *", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    last_retrieved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    retrievals: Mapped[list[Retrieval]] = relationship(
        "Retrieval", back_populates="source", cascade="all, delete-orphan"
    )
    scholarships: Mapped[list[Scholarship]] = relationship("Scholarship", back_populates="source")


class Retrieval(Base):
    __tablename__ = "retrievals"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_id: Mapped[str] = mapped_column(
        String, ForeignKey("sources.id", ondelete="CASCADE"), index=True, nullable=False
    )
    url: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # Status e.g. success, failed, timeout, uncertain
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False, index=True)
    http_status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    source: Mapped[Source] = relationship("Source", back_populates="retrievals")
    scholarship_versions: Mapped[list[ScholarshipVersion]] = relationship(
        "ScholarshipVersion", back_populates="retrieval"
    )

    __table_args__ = (Index("ix_retrievals_source_url_hash", "source_id", "url", "content_hash"),)


class RetrievalProcessingClaim(Base):
    """
    Atomic processing claim record at the crawler processing boundary.
    Enforces uniqueness for (source_id, url, content_hash) to guarantee
    that duplicate updates with identical non-null content hashes are not re-processed.
    """

    __tablename__ = "retrieval_processing_claims"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_id: Mapped[str] = mapped_column(
        String, ForeignKey("sources.id", ondelete="CASCADE"), index=True, nullable=False
    )
    url: Mapped[str] = mapped_column(String, nullable=False, index=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    claimed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "url",
            "content_hash",
            name="uq_retrieval_processing_claims",
        ),
    )


class Scholarship(Base):
    __tablename__ = "scholarships"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("sources.id", ondelete="SET NULL"), index=True, nullable=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String, nullable=False, index=True)
    official_portal_url: Mapped[str] = mapped_column(String, nullable=False)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String, default="open", nullable=False, index=True)
    # Rule 4: "fresh" or "uncertain"
    freshness: Mapped[str] = mapped_column(String, default="fresh", nullable=False, index=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    source: Mapped[Source | None] = relationship("Source", back_populates="scholarships")
    versions: Mapped[list[ScholarshipVersion]] = relationship(
        "ScholarshipVersion", back_populates="scholarship", cascade="all, delete-orphan"
    )


class ScholarshipVersion(Base):
    """
    Revision snapshot representing a published or under-review scholarship specification.
    uq_scholarship_cycle_version enforces unique version numbers per cycle.
    Immutability of approved versions is enforced by the before_update event listener.
    """

    __tablename__ = "scholarship_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    scholarship_id: Mapped[str] = mapped_column(
        String, ForeignKey("scholarships.id", ondelete="CASCADE"), index=True, nullable=False
    )
    retrieval_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("retrievals.id", ondelete="SET NULL"), index=True, nullable=True
    )
    application_cycle: Mapped[str] = mapped_column(String, nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    coverage_details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        String, default=VersionStatus.DRAFT.value, nullable=False, index=True
    )
    raw_extracted_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(
        String, ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    scholarship: Mapped[Scholarship] = relationship("Scholarship", back_populates="versions")
    retrieval: Mapped[Retrieval | None] = relationship(
        "Retrieval", back_populates="scholarship_versions"
    )
    requirements: Mapped[list[Requirement]] = relationship(
        "Requirement", back_populates="scholarship_version", cascade="all, delete-orphan"
    )
    required_documents: Mapped[list[RequiredDocument]] = relationship(
        "RequiredDocument", back_populates="scholarship_version", cascade="all, delete-orphan"
    )
    evidence_checks: Mapped[list[EvidenceCheck]] = relationship(
        "EvidenceCheck",
        back_populates="scholarship_version",
        cascade="all, delete-orphan",
        overlaps="evidence_checks,requirement",
    )

    __table_args__ = (
        UniqueConstraint(
            "scholarship_id",
            "application_cycle",
            "version_number",
            name="uq_scholarship_cycle_version",
        ),
    )


@event.listens_for(ScholarshipVersion, "before_update")
def enforce_approved_version_immutability(
    mapper: Any, connection: Any, target: ScholarshipVersion
) -> None:
    """
    Prevents modifying content fields of an approved version snapshot.
    Review transitions on unapproved versions remain permitted.
    """
    stmt = select(
        ScholarshipVersion.status,
        ScholarshipVersion.title,
        ScholarshipVersion.description,
        ScholarshipVersion.coverage_details,
        ScholarshipVersion.deadline,
        ScholarshipVersion.application_cycle,
        ScholarshipVersion.version_number,
        ScholarshipVersion.raw_extracted_data,
    ).where(ScholarshipVersion.id == target.id)
    prev = connection.execute(stmt).first()
    if prev and prev[0] == VersionStatus.APPROVED.value:
        content_changed = (
            target.title != prev[1]
            or target.description != prev[2]
            or target.coverage_details != prev[3]
            or target.deadline != prev[4]
            or target.application_cycle != prev[5]
            or target.version_number != prev[6]
            or target.raw_extracted_data != prev[7]
        )
        if content_changed:
            raise ValueError(
                f"Approved scholarship version '{target.id}' is immutable. "
                "Content modifications must be published as a new version."
            )

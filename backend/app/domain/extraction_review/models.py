"""
SQLAlchemy models for Extraction and Evidence Review domain.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ExtractionReview(Base):
    __tablename__ = "extraction_reviews"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    scholarship_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    source_url: Mapped[str] = mapped_column(String, nullable=False)
    extracted_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    jev_evidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    jev_evidence_verdict: Mapped[str | None] = mapped_column(String, nullable=True)
    # Rule 3: Jev results assist the administrator and never auto-publish.
    review_status: Mapped[str] = mapped_column(String, default="pending_review", nullable=False)
    admin_notes: Mapped[str | None] = mapped_column(String, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String, nullable=True)

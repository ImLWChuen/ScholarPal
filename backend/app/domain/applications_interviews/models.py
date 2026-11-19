"""
SQLAlchemy models for Applications and Interviews domain.
Rule 7: Never auto-submitted.
Rule 8: student_id index for strict ownership enforcement.
"""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class StudentApplication(Base):
    __tablename__ = "student_applications"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    # Rule 8: Mandatory student_id for ownership enforcement
    student_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    scholarship_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    # Rule 7: Never marked submitted automatically
    stage: Mapped[str] = mapped_column(String, default="drafting", nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    portal_submission_reference: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

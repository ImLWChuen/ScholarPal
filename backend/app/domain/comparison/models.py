"""
SQLAlchemy models for Comparison domain.
"""

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ComparisonSet(Base):
    __tablename__ = "comparison_sets"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    # Rule 8: student ownership
    student_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    scholarship_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

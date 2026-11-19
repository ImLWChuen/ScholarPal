"""
SQLAlchemy models for Profile and Preparation domain.
"""

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    education_level: Mapped[str | None] = mapped_column(String, nullable=True)
    citizenship: Mapped[str | None] = mapped_column(String, nullable=True)
    state_of_origin: Mapped[str | None] = mapped_column(String, nullable=True)
    # Rule 5: Unknown values stay unknown (NULL), never zero
    household_income: Mapped[float | None] = mapped_column(Float, nullable=True)
    cgpa: Mapped[float | None] = mapped_column(Float, nullable=True)

"""
SQLAlchemy models for Eligibility and Change Impact domain.
Rule 1: Predefined rules stored deterministically.
"""

from typing import Any

from sqlalchemy import JSON, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    scholarship_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    criterion_code: Mapped[str] = mapped_column(String, nullable=False)
    rule_type: Mapped[str] = mapped_column(String, nullable=False)
    rule_parameters: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

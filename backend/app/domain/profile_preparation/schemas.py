"""
Profile and Preparation Domain Module.
Covers student profile (academic records, income, co-curriculars, citizenship, state).
Non-negotiable rule 5: Unknown values stay unknown (None/null), never zero.
Non-negotiable rule 8: Strict data segregation by student_id.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.common_validators import (
    normalize_and_validate_study_level,
    validate_academic_results_dict,
    validate_cgpa_range,
    validate_non_negative_income,
)
from app.domain.shared_enums import UserRole


# ---------------------------------------------------------------------------
# User Models
# ---------------------------------------------------------------------------
class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str = Field(..., max_length=255, description="User email address")
    full_name: str = Field(..., min_length=1, max_length=255)
    role: UserRole = UserRole.STUDENT
    is_active: bool = True
    is_verified: bool = False


class UserCreate(UserBase):
    id: str | None = None
    password: str = Field(default="", min_length=0)


class UserUpdate(BaseModel):
    email: str | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    role: UserRole | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class UserRead(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Student Profile Models
# ---------------------------------------------------------------------------
class StudentProfileBase(BaseModel):
    """
    Student academic and demographic profile.
    Rule 5: household_income stays None when unknown; never default to 0.
    """

    model_config = ConfigDict(from_attributes=True)

    user_id: str
    study_level: str | None = Field(
        default=None,
        description="Standard study level (Secondary, Pre-University, Undergraduate, Postgraduate)",
    )
    education_level: str | None = Field(
        default=None,
        description="Legacy alias for study level",
    )
    nationality: str | None = Field(default=None, max_length=100)
    citizenship: str | None = Field(default=None, max_length=100)
    state_of_origin: str | None = Field(default=None, max_length=100)
    field_of_study: str | None = Field(default=None, max_length=200)
    intended_field: str | None = Field(default=None, max_length=200)
    academic_results: dict[str, Any] | None = Field(
        default=None,
        description="Grades mapping (e.g. {'BM': 'A+', 'Math': 'A'})",
    )
    household_income: float | None = Field(
        default=None,
        ge=0.0,
        description="Gross monthly household income in MYR. None when unknown.",
    )
    cgpa: float | None = Field(
        default=None,
        ge=0.0,
        le=4.0,
        description="Cumulative Grade Point Average (0.00 to 4.00 inclusive)",
    )

    @field_validator("cgpa", mode="before")
    @classmethod
    def check_cgpa(cls, v: Any) -> float | None:
        return validate_cgpa_range(v)

    @field_validator("household_income", mode="before")
    @classmethod
    def check_income(cls, v: Any) -> float | None:
        return validate_non_negative_income(v)

    @field_validator("study_level", "education_level", mode="before")
    @classmethod
    def check_study_level(cls, v: Any) -> str | None:
        return normalize_and_validate_study_level(v)

    @field_validator("academic_results", mode="before")
    @classmethod
    def check_results(cls, v: Any) -> dict[str, Any] | None:
        return validate_academic_results_dict(v)


class StudentProfileCreate(StudentProfileBase):
    id: str | None = None


class StudentProfileUpdate(BaseModel):
    study_level: str | None = None
    education_level: str | None = None
    nationality: str | None = None
    citizenship: str | None = None
    state_of_origin: str | None = None
    field_of_study: str | None = None
    intended_field: str | None = None
    academic_results: dict[str, Any] | None = None
    household_income: float | None = Field(default=None, ge=0.0)
    cgpa: float | None = Field(default=None, ge=0.0, le=4.0)

    @field_validator("cgpa", mode="before")
    @classmethod
    def check_cgpa(cls, v: Any) -> float | None:
        return validate_cgpa_range(v)

    @field_validator("household_income", mode="before")
    @classmethod
    def check_income(cls, v: Any) -> float | None:
        return validate_non_negative_income(v)

    @field_validator("study_level", "education_level", mode="before")
    @classmethod
    def check_study_level(cls, v: Any) -> str | None:
        return normalize_and_validate_study_level(v)

    @field_validator("academic_results", mode="before")
    @classmethod
    def check_results(cls, v: Any) -> dict[str, Any] | None:
        return validate_academic_results_dict(v)


class StudentProfileRead(StudentProfileBase):
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

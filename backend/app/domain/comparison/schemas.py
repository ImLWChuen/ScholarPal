"""
Comparison Domain Module.
Covers side-by-side matrix comparisons of scholarships (allowances, bond durations, eligibility).
Rule 8: Record ownership on student saved comparison sets.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ScholarshipComparisonItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scholarship_id: str
    title: str
    provider: str
    bond_duration_months: int | None = None
    monthly_allowance: float | None = None
    tuition_covered: bool | None = None
    eligibility_summary: str | None = None


class ComparisonSetBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: str
    name: str = Field(..., min_length=1, max_length=255)
    scholarship_ids: list[str] = Field(default_factory=list)


class ComparisonSetCreate(ComparisonSetBase):
    id: str | None = None


class ComparisonSetUpdate(BaseModel):
    name: str | None = None
    scholarship_ids: list[str] | None = None


class ComparisonSetRead(ComparisonSetBase):
    id: str
    created_at: datetime
    updated_at: datetime

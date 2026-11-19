"""
Comparison Domain Module.
Covers side-by-side matrix comparisons of scholarships (allowances, bond durations, eligibility).
Rule 8: Record ownership on student saved comparison sets.
"""

from pydantic import BaseModel, ConfigDict


class ScholarshipComparisonItem(BaseModel):
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
    name: str
    scholarship_ids: list[str]

"""
Profile and Preparation Domain Module.
Covers student profile (academic records, income, co-curriculars, citizenship, state).
Non-negotiable rule 5: Unknown values stay unknown (None/null), never zero.
"""

from pydantic import BaseModel, ConfigDict


class StudentProfileBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    education_level: str | None = None  # Secondary, Pre-U, Undergrad, Postgrad
    citizenship: str | None = None
    state_of_origin: str | None = None
    household_income: float | None = None  # None when unknown, NEVER 0 unless explicitly 0
    cgpa: float | None = None

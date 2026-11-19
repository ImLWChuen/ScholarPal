"""
Eligibility and Change Impact Domain Module.
Non-negotiable rule 1: Eligibility results come only from predefined rules, never from an LLM.
Non-negotiable rule 2: Each requirement is satisfied, unmet or unresolved;
overall result is:
- Does not meet recorded requirements (any mandatory unmet)
- Needs clarification (none unmet but something missing or unclear)
- Meets recorded requirements (all mandatory satisfied)
Non-negotiable rule 6: What-if checks never modify saved data (ephemeral evaluation).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.domain.shared_enums import (
    OverallEligibility,
    RequirementOutcome,
)

# Backward-compatibility aliases
RequirementState = RequirementOutcome
OverallEligibilityResult = OverallEligibility


# ---------------------------------------------------------------------------
# Requirement Schemas
# ---------------------------------------------------------------------------
class RequirementBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scholarship_version_id: str
    type: str = Field(
        ...,
        description="Requirement dimension e.g. academic_cgpa, nationality, study_level",
    )
    operator: str = Field(..., description="Comparison operator: eq, gte, lte, in, contains")
    value: Any = Field(..., description="Target threshold or qualifying criterion")
    is_mandatory: bool = True
    source_excerpt: str | None = None
    is_subjective: bool = False


class RequirementCreate(RequirementBase):
    id: str | None = None


class RequirementUpdate(BaseModel):
    type: str | None = None
    operator: str | None = None
    value: Any | None = None
    is_mandatory: bool | None = None
    source_excerpt: str | None = None
    is_subjective: bool | None = None


class RequirementRead(RequirementBase):
    id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Evaluation & Simulation Schemas
# ---------------------------------------------------------------------------
class RequirementEvaluation(BaseModel):
    requirement_id: str
    criterion_name: str
    is_mandatory: bool = True
    state: RequirementOutcome
    reason: str


class EligibilityEvaluationRequest(BaseModel):
    scholarship_id: str
    student_id: str | None = None
    # For ephemeral what-if simulation (Rule 6: Never modifies saved data)
    simulation_profile: dict[str, Any] | None = None


class EligibilityEvaluationResult(BaseModel):
    scholarship_id: str
    student_id: str
    overall_result: OverallEligibility
    evaluations: list[RequirementEvaluation]
    is_simulation: bool = False  # Rule 6: What-if checks are ephemeral simulations
    evaluated_at: datetime | None = None


# ---------------------------------------------------------------------------
# Legacy Compatibility Models
# ---------------------------------------------------------------------------
class EligibilityRuleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scholarship_id: str
    criterion_code: str
    rule_type: str
    rule_parameters: dict[str, Any]
    is_mandatory: bool = True


class EligibilityRuleCreate(EligibilityRuleBase):
    id: str | None = None


class EligibilityRuleUpdate(BaseModel):
    criterion_code: str | None = None
    rule_type: str | None = None
    rule_parameters: dict[str, Any] | None = None
    is_mandatory: bool | None = None


class EligibilityRuleRead(EligibilityRuleBase):
    id: str

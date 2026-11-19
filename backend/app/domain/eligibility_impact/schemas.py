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

from enum import Enum

from pydantic import BaseModel, ConfigDict


class RequirementState(str, Enum):
    SATISFIED = "satisfied"
    UNMET = "unmet"
    UNRESOLVED = "unresolved"


class OverallEligibilityResult(str, Enum):
    DOES_NOT_MEET = "Does not meet recorded requirements"
    NEEDS_CLARIFICATION = "Needs clarification"
    MEETS_REQUIREMENTS = "Meets recorded requirements"


class RequirementEvaluation(BaseModel):
    requirement_id: str
    criterion_name: str
    is_mandatory: bool = True
    state: RequirementState
    reason: str


class EligibilityEvaluationResult(BaseModel):
    scholarship_id: str
    student_id: str
    overall_result: OverallEligibilityResult
    evaluations: list[RequirementEvaluation]
    is_simulation: bool = False  # Rule 6: What-if checks are ephemeral simulations


class EligibilityRuleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scholarship_id: str
    criterion_code: str
    rule_type: str  # e.g., min_cgpa, household_income_max, state, nationality
    rule_parameters: dict
    is_mandatory: bool = True

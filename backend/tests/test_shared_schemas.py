"""
Tests for ScholarPal shared schemas, domain enums, and validation rules.
Verifies GPA range enforcement, non-negative income checks, study level normalization,
academic grade validation, and OpenAPI schema consistency.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.domain.common_validators import (
    normalize_and_validate_study_level,
    validate_academic_results_dict,
    validate_cgpa_range,
    validate_grade_value,
    validate_non_negative_income,
)
from app.domain.profile_preparation.schemas import (
    StudentProfileCreate,
)
from app.domain.schemas import ALL_DOMAIN_ENUMS, ALL_DOMAIN_SCHEMAS
from app.domain.shared_enums import (
    ApplicationStage,
    EvidenceLabel,
    OverallEligibility,
    RequirementOutcome,
    StudyLevel,
    UserRole,
    VersionStatus,
)
from app.main import app


# ---------------------------------------------------------------------------
# Enum Tests
# ---------------------------------------------------------------------------
def test_shared_enums_values():
    # Requirement outcome: satisfied, unmet, unresolved
    assert RequirementOutcome.SATISFIED.value == "satisfied"
    assert RequirementOutcome.UNMET.value == "unmet"
    assert RequirementOutcome.UNRESOLVED.value == "unresolved"

    # Overall eligibility: 3 canonical deterministic states
    assert OverallEligibility.DOES_NOT_MEET.value == "Does not meet recorded requirements"
    assert OverallEligibility.NEEDS_CLARIFICATION.value == "Needs clarification"
    assert OverallEligibility.MEETS_REQUIREMENTS.value == "Meets recorded requirements"

    # Application stage: Saved, Preparing, Submitted, Interview, Offered, Unsuccessful, Withdrawn
    stages = [s.value for s in ApplicationStage]
    assert stages == [
        "Saved",
        "Preparing",
        "Submitted",
        "Interview",
        "Offered",
        "Unsuccessful",
        "Withdrawn",
    ]

    # Version status: draft, pending, approved, rejected, deferred
    statuses = [v.value for v in VersionStatus]
    assert statuses == ["draft", "pending", "approved", "rejected", "deferred"]

    # Evidence label: supported, contradicted, unclear
    labels = [e.value for e in EvidenceLabel]
    assert labels == ["supported", "contradicted", "unclear"]

    # Study levels: Secondary, Pre-University, Undergraduate, Postgraduate
    levels = [s.value for s in StudyLevel]
    assert levels == [
        "Secondary",
        "Pre-University",
        "Undergraduate",
        "Postgraduate",
    ]

    # UserRole: student, administrator
    assert UserRole.STUDENT.value == "student"
    assert UserRole.ADMINISTRATOR.value == "administrator"


# ---------------------------------------------------------------------------
# GPA / CGPA Validation Tests
# ---------------------------------------------------------------------------
def test_cgpa_validation_valid():
    # Boundary values and standard values
    assert validate_cgpa_range(0.0) == 0.0
    assert validate_cgpa_range(4.0) == 4.0
    assert validate_cgpa_range(3.75) == 3.75
    assert validate_cgpa_range("3.85") == 3.85
    assert validate_cgpa_range(None) is None

    profile = StudentProfileCreate(user_id="u1", cgpa=3.85)
    assert profile.cgpa == 3.85


def test_cgpa_validation_out_of_range():
    # Greater than 4.0
    with pytest.raises(ValidationError, match="between 0.00 and 4.00"):
        StudentProfileCreate(user_id="u1", cgpa=4.01)

    # Negative CGPA
    with pytest.raises(ValidationError, match="between 0.00 and 4.00"):
        StudentProfileCreate(user_id="u1", cgpa=-0.05)

    with pytest.raises(ValueError, match="between 0.00 and 4.00"):
        validate_cgpa_range(5.0)


# ---------------------------------------------------------------------------
# Household Income Validation Tests
# ---------------------------------------------------------------------------
def test_household_income_validation_valid():
    # Rule 5: None must be preserved when unknown
    profile_none = StudentProfileCreate(user_id="u1", household_income=None)
    assert profile_none.household_income is None

    # Zero income is valid if explicitly 0
    profile_zero = StudentProfileCreate(user_id="u1", household_income=0.0)
    assert profile_zero.household_income == 0.0

    # Positive income
    profile_pos = StudentProfileCreate(user_id="u1", household_income=4500.50)
    assert profile_pos.household_income == 4500.50


def test_household_income_validation_negative():
    # Negative income must be rejected
    with pytest.raises(ValidationError, match="cannot be negative"):
        StudentProfileCreate(user_id="u1", household_income=-1.0)

    with pytest.raises(ValueError, match="cannot be negative"):
        validate_non_negative_income(-500.0)


# ---------------------------------------------------------------------------
# Study Level Validation Tests
# ---------------------------------------------------------------------------
def test_study_level_validation_valid():
    assert normalize_and_validate_study_level("Secondary") == StudyLevel.SECONDARY.value
    assert normalize_and_validate_study_level("SPM") == StudyLevel.SECONDARY.value
    assert normalize_and_validate_study_level("Pre-University") == StudyLevel.PRE_UNIVERSITY.value
    assert normalize_and_validate_study_level("STPM") == StudyLevel.PRE_UNIVERSITY.value
    assert normalize_and_validate_study_level("Matriculation") == StudyLevel.PRE_UNIVERSITY.value
    assert normalize_and_validate_study_level("A-Levels") == StudyLevel.PRE_UNIVERSITY.value
    assert normalize_and_validate_study_level("Undergraduate") == StudyLevel.UNDERGRADUATE.value
    assert normalize_and_validate_study_level("Degree") == StudyLevel.UNDERGRADUATE.value
    assert normalize_and_validate_study_level("Bachelor") == StudyLevel.UNDERGRADUATE.value
    assert normalize_and_validate_study_level("Postgraduate") == StudyLevel.POSTGRADUATE.value
    assert normalize_and_validate_study_level("Masters") == StudyLevel.POSTGRADUATE.value
    assert normalize_and_validate_study_level("PhD") == StudyLevel.POSTGRADUATE.value
    assert normalize_and_validate_study_level(None) is None

    profile = StudentProfileCreate(user_id="u1", study_level="Degree")
    assert profile.study_level == StudyLevel.UNDERGRADUATE.value


def test_study_level_validation_invalid():
    with pytest.raises(ValidationError, match="Invalid study level"):
        StudentProfileCreate(user_id="u1", study_level="Kindergarten")

    with pytest.raises(ValueError, match="Invalid study level"):
        normalize_and_validate_study_level("PrimarySchool")


# ---------------------------------------------------------------------------
# Academic Grade Validation Tests
# ---------------------------------------------------------------------------
def test_academic_results_grade_validation():
    # Valid letter grades
    assert validate_grade_value("A+") == "A+"
    assert validate_grade_value("A") == "A"
    assert validate_grade_value("B") == "B"
    assert validate_grade_value("C+") == "C+"
    assert validate_grade_value("G") == "G"

    # Valid percentage / numeric scores
    assert validate_grade_value(95) == 95.0
    assert validate_grade_value("85") == 85.0
    assert validate_grade_value(3.8) == 3.8

    # Valid nested dictionary
    valid_results = {
        "spm": {"Bahasa Melayu": "A+", "Mathematics": "A", "English": "A-"},
        "co_curricular": 88,
    }
    validated = validate_academic_results_dict(valid_results)
    assert validated == valid_results

    profile = StudentProfileCreate(user_id="u1", academic_results=valid_results)
    assert profile.academic_results == valid_results

    # Invalid letter grade
    with pytest.raises(ValidationError, match="Invalid grade value"):
        StudentProfileCreate(user_id="u1", academic_results={"Math": "Z_INVALID"})

    # Out-of-bounds numeric grade
    with pytest.raises(ValidationError, match="Numeric grade score must be 0-100"):
        StudentProfileCreate(user_id="u1", academic_results={"Math": 150})


# ---------------------------------------------------------------------------
# OpenAPI Schema Completeness & Registry Tests
# ---------------------------------------------------------------------------
def test_openapi_schema_contains_all_models_and_enums():
    openapi_dict = app.openapi()
    schemas = openapi_dict["components"]["schemas"]

    # Verify all shared enums exist
    for enum_cls in ALL_DOMAIN_ENUMS:
        assert enum_cls.__name__ in schemas, f"Enum {enum_cls.__name__} missing in OpenAPI schemas"
        enum_def = schemas[enum_cls.__name__]
        assert "enum" in enum_def
        expected_values = [item.value for item in enum_cls]
        assert set(enum_def["enum"]) == set(expected_values)

    # Verify core domain models exist
    for model in ALL_DOMAIN_SCHEMAS:
        assert model.__name__ in schemas, f"Model {model.__name__} missing in OpenAPI schemas"

    # Check key models explicitly
    assert "StudentProfileRead" in schemas
    assert "ScholarshipRead" in schemas
    assert "ApplicationRead" in schemas
    assert "EvidenceCheckRead" in schemas
    assert "EligibilityEvaluationResult" in schemas

"""
Reusable validation logic for ScholarPal Pydantic models.
Enforces non-negative income, CGPA ranges, recognized academic grades, and valid study levels.
"""

from __future__ import annotations

import re
from typing import Any

from app.domain.shared_enums import StudyLevel

VALID_STUDY_LEVEL_NAMES = {s.value.lower(): s.value for s in StudyLevel}

STUDY_LEVEL_ALIASES: dict[str, str] = {
    "secondary": StudyLevel.SECONDARY.value,
    "spm": StudyLevel.SECONDARY.value,
    "o-level": StudyLevel.SECONDARY.value,
    "o levels": StudyLevel.SECONDARY.value,
    "pre-u": StudyLevel.PRE_UNIVERSITY.value,
    "pre-university": StudyLevel.PRE_UNIVERSITY.value,
    "stpm": StudyLevel.PRE_UNIVERSITY.value,
    "matriculation": StudyLevel.PRE_UNIVERSITY.value,
    "matrikulasi": StudyLevel.PRE_UNIVERSITY.value,
    "foundation": StudyLevel.PRE_UNIVERSITY.value,
    "a-level": StudyLevel.PRE_UNIVERSITY.value,
    "a-levels": StudyLevel.PRE_UNIVERSITY.value,
    "diploma": StudyLevel.PRE_UNIVERSITY.value,
    "undergraduate": StudyLevel.UNDERGRADUATE.value,
    "undergrad": StudyLevel.UNDERGRADUATE.value,
    "degree": StudyLevel.UNDERGRADUATE.value,
    "bachelor": StudyLevel.UNDERGRADUATE.value,
    "bachelors": StudyLevel.UNDERGRADUATE.value,
    "postgraduate": StudyLevel.POSTGRADUATE.value,
    "postgrad": StudyLevel.POSTGRADUATE.value,
    "master": StudyLevel.POSTGRADUATE.value,
    "masters": StudyLevel.POSTGRADUATE.value,
    "phd": StudyLevel.POSTGRADUATE.value,
    "doctorate": StudyLevel.POSTGRADUATE.value,
}

# Recognized Malaysian and International academic grades
VALID_LETTER_GRADES = {
    # SPM / SPMV
    "A+",
    "A",
    "A-",
    "B+",
    "B",
    "C+",
    "C",
    "D",
    "E",
    "G",
    "TH",
    # STPM / Pre-U / Matriculation
    "B-",
    "C-",
    "D+",
    "F",
    # A-Level
    "A*",
    "U",
}


def normalize_and_validate_study_level(val: Any) -> str | None:
    """
    Validates and normalizes study level strings to one of StudyLevel enum values.
    Raises ValueError for unrecognized study levels.
    """
    if val is None:
        return None
    raw = str(val).strip()
    if not raw:
        return None

    cleaned = raw.lower()
    if cleaned in STUDY_LEVEL_ALIASES:
        return STUDY_LEVEL_ALIASES[cleaned]
    if cleaned in VALID_STUDY_LEVEL_NAMES:
        return VALID_STUDY_LEVEL_NAMES[cleaned]

    allowed = [s.value for s in StudyLevel]
    raise ValueError(f"Invalid study level '{raw}'. Must be one of: {', '.join(allowed)}")


def validate_cgpa_range(val: Any) -> float | None:
    """
    Validates that CGPA is between 0.00 and 4.00 inclusive.
    """
    if val is None:
        return None
    try:
        f_val = float(val)
    except (TypeError, ValueError) as err:
        raise ValueError(f"CGPA must be a valid number, got '{val}'") from err

    if f_val < 0.0 or f_val > 4.0:
        raise ValueError(f"CGPA must be between 0.00 and 4.00 inclusive, got {f_val}")
    return round(f_val, 2)


def validate_non_negative_income(val: Any) -> float | None:
    """
    Validates that household income is non-negative.
    Preserves None when unknown (Rule 5: Unknown values stay unknown, never 0).
    """
    if val is None:
        return None
    try:
        f_val = float(val)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Household income must be a valid number, got '{val}'") from err

    if f_val < 0.0:
        raise ValueError(f"Household income cannot be negative, got {f_val}")
    return round(f_val, 2)


def validate_grade_value(grade: Any) -> str | float:
    """
    Validates a single grade value (letter grade e.g. 'A+', 'B' or percentage score 0-100).
    """
    if grade is None:
        raise ValueError("Grade value cannot be null.")

    # Check if numeric score
    if isinstance(grade, (int, float)):
        if 0 <= grade <= 100:
            return float(grade)
        if 0.0 <= grade <= 4.0:
            return float(grade)
        raise ValueError(f"Numeric grade score must be 0-100 or 0.0-4.0, got {grade}")

    raw = str(grade).strip().upper()
    if raw in VALID_LETTER_GRADES:
        return raw

    # Check numeric string (e.g. "85" or "3.8")
    if re.match(r"^\d+(\.\d+)?$", raw):
        num = float(raw)
        if 0 <= num <= 100:
            return num
        raise ValueError(f"Numeric grade score must be between 0 and 100, got {num}")

    raise ValueError(
        f"Invalid grade value '{grade}'. Must be a recognized letter grade "
        "(e.g. A+, A, A-, B) or score 0-100."
    )


def validate_academic_results_dict(results: Any) -> dict[str, Any] | None:
    """
    Validates academic results structure.
    Accepts flat subject->grade mapping or nested curriculum->subject->grade mapping.
    """
    if results is None:
        return None
    if not isinstance(results, dict):
        raise ValueError("academic_results must be a JSON object / dictionary.")

    for _k, v in results.items():
        if isinstance(v, dict):
            # Nested e.g. {"spm": {"BM": "A+", "Math": "A"}}
            for _subj, grade in v.items():
                validate_grade_value(grade)
        elif v is not None:
            # Flat e.g. {"BM": "A+", "Math": "A"}
            validate_grade_value(v)

    return results

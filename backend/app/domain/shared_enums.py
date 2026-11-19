"""
Shared domain enums for ScholarPal.
Single source of truth for API models, business logic, and generated TypeScript types.
"""

from enum import Enum


class RequirementOutcome(str, Enum):
    """
    Outcome for an individual requirement evaluation.
    Rule 2: Derived strictly from deterministic rules; never an LLM.
    """

    SATISFIED = "satisfied"
    UNMET = "unmet"
    UNRESOLVED = "unresolved"


class OverallEligibility(str, Enum):
    """
    Overall student eligibility result for a scholarship.
    Rule 2: Derived strictly from deterministic rules; never an LLM.
    """

    DOES_NOT_MEET = "Does not meet recorded requirements"
    NEEDS_CLARIFICATION = "Needs clarification"
    MEETS_REQUIREMENTS = "Meets recorded requirements"


class ApplicationStage(str, Enum):
    """
    Student application pipeline stages.
    Rule 7: Student submits on provider portals; ScholarPal never auto-submits.
    """

    SAVED = "Saved"
    PREPARING = "Preparing"
    SUBMITTED = "Submitted"
    INTERVIEW = "Interview"
    OFFERED = "Offered"
    UNSUCCESSFUL = "Unsuccessful"
    WITHDRAWN = "Withdrawn"


class VersionStatus(str, Enum):
    """Review lifecycle status for scholarship version snapshots."""

    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"


class EvidenceLabel(str, Enum):
    """
    Jev evidence verification label for extracted scholarship requirements.
    Rule 3: Jev results assist the administrator and never auto-publish.
    """

    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    UNCLEAR = "unclear"


class StudyLevel(str, Enum):
    """Standardized academic study levels in Malaysian higher education."""

    SECONDARY = "Secondary"
    PRE_UNIVERSITY = "Pre-University"
    UNDERGRADUATE = "Undergraduate"
    POSTGRADUATE = "Postgraduate"


class UserRole(str, Enum):
    """User access control roles."""

    STUDENT = "student"
    ADMINISTRATOR = "administrator"


class FreshnessStatus(str, Enum):
    """
    Scholarship data freshness status.
    Rule 4: Stale scholarship data is worse than no data.
    """

    FRESH = "fresh"
    UNCERTAIN = "uncertain"


class ScholarshipStatus(str, Enum):
    """Current portal availability status for a scholarship."""

    OPEN = "open"
    CLOSED = "closed"
    UPCOMING = "upcoming"


class RetrievalStatus(str, Enum):
    """Crawl/retrieval execution status."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

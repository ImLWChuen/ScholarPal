"""
Applications and Interviews Domain Module.
Covers student application tracking, interview milestones, checklist, and deadlines.
Non-negotiable rule 7: Students submit on official provider portals;
ScholarPal never marks submission automatically (requires explicit student action/confirmation).
Non-negotiable rule 8: Backend enforces record ownership on every student endpoint.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ApplicationStage(str, Enum):
    DRAFTING = "drafting"
    READY_TO_SUBMIT = "ready_to_submit"
    SUBMITTED_BY_STUDENT = "submitted_by_student"  # Explicitly marked by student, NEVER automatic
    INTERVIEW_INVITED = "interview_invited"
    COMPLETED = "completed"


class StudentApplicationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: str
    scholarship_id: str
    stage: ApplicationStage = ApplicationStage.DRAFTING
    submitted_at: datetime | None = None  # Confirmed timestamp by student
    portal_submission_reference: str | None = None
    notes: str | None = None

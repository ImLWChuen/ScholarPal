from __future__ import annotations

from app.domain.applications_interviews.models import Application, Interview
from app.repositories.base import ScopedRepository


class InterviewRepository(ScopedRepository[Interview]):
    """Repository for application interview records scoped via application.student_id."""

    def __init__(self) -> None:
        super().__init__(
            model=Interview,
            parent_model=Application,
            parent_fk="application_id",
            parent_owner_field="student_id",
        )


interview_repository = InterviewRepository()

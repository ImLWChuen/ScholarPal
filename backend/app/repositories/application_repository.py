from __future__ import annotations

from app.domain.applications_interviews.models import Application
from app.repositories.base import ScopedRepository


class ApplicationRepository(ScopedRepository[Application]):
    """Repository for scholarship application records scoped by student_id."""

    def __init__(self) -> None:
        super().__init__(model=Application, owner_field="student_id")


application_repository = ApplicationRepository()


from __future__ import annotations

from app.domain.applications_interviews.models import Application, ApplicationTask
from app.repositories.base import ScopedRepository


class TaskRepository(ScopedRepository[ApplicationTask]):
    """Repository for application task records scoped via application.student_id."""

    def __init__(self) -> None:
        super().__init__(
            model=ApplicationTask,
            parent_model=Application,
            parent_fk="application_id",
            parent_owner_field="student_id",
        )


task_repository = TaskRepository()


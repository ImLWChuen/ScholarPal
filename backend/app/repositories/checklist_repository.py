from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.applications_interviews.models import Application, DocumentChecklistItem
from app.repositories.base import ScopedRepository


class ChecklistRepository(ScopedRepository[DocumentChecklistItem]):
    """Repository for application document checklist items scoped via application.student_id."""

    def __init__(self) -> None:
        super().__init__(
            model=DocumentChecklistItem,
            parent_model=Application,
            parent_fk="application_id",
            parent_owner_field="student_id",
        )

    async def list_by_application_scoped(
        self, db: AsyncSession, application_id: str, user_id: str
    ) -> list[DocumentChecklistItem]:
        """List checklist items for an application strictly scoped to the authenticated student."""
        stmt = select(self.model).where(self.model.application_id == application_id)
        stmt = self.apply_ownership_scope(stmt, user_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_app_and_id_scoped(
        self, db: AsyncSession, application_id: str, item_id: str, user_id: str
    ) -> DocumentChecklistItem | None:
        """Fetch a checklist item by application_id and item_id scoped to the student."""
        stmt = select(self.model).where(
            self.model.application_id == application_id,
            self.model.id == item_id,
        )
        stmt = self.apply_ownership_scope(stmt, user_id)
        result = await db.execute(stmt)
        return result.scalars().first()


checklist_repository = ChecklistRepository()

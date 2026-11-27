from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.audit_notifications.models import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for append-only audit log entries."""

    def __init__(self) -> None:
        super().__init__(model=AuditLog)

    async def record_event(
        self,
        db: AsyncSession,
        *,
        actor_id: str | None,
        action: str,
        entity_type: str,
        entity_id: str,
        changes: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        """Append an immutable audit log entry."""
        entry = AuditLog(
            id=f"aud_{uuid.uuid4().hex[:12]}",
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            ip_address=ip_address,
        )
        return await self.create(db, entry)


audit_log_repository = AuditLogRepository()

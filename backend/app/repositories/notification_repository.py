from __future__ import annotations

from app.domain.audit_notifications.models import Notification
from app.repositories.base import ScopedRepository


class NotificationRepository(ScopedRepository[Notification]):
    """Repository for in-app notification records scoped by user_id."""

    def __init__(self) -> None:
        super().__init__(model=Notification, owner_field="user_id")


notification_repository = NotificationRepository()

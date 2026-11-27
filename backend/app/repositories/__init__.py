from __future__ import annotations

from app.repositories.application_repository import (
    ApplicationRepository,
    application_repository,
)
from app.repositories.audit_repository import (
    AuditLogRepository,
    audit_log_repository,
)
from app.repositories.base import BaseRepository, ScopedRepository
from app.repositories.checklist_repository import (
    ChecklistRepository,
    checklist_repository,
)
from app.repositories.interview_repository import (
    InterviewRepository,
    interview_repository,
)
from app.repositories.notification_repository import (
    NotificationRepository,
    notification_repository,
)
from app.repositories.offer_repository import (
    OfferRepository,
    offer_repository,
)
from app.repositories.profile_repository import (
    ProfileRepository,
    profile_repository,
)
from app.repositories.task_repository import (
    TaskRepository,
    task_repository,
)

__all__ = [
    "ApplicationRepository",
    "AuditLogRepository",
    "BaseRepository",
    "ChecklistRepository",
    "InterviewRepository",
    "NotificationRepository",
    "OfferRepository",
    "ProfileRepository",
    "ScopedRepository",
    "TaskRepository",
    "application_repository",
    "audit_log_repository",
    "checklist_repository",
    "interview_repository",
    "notification_repository",
    "offer_repository",
    "profile_repository",
    "task_repository",
]

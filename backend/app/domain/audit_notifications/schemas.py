"""
Audit and Notifications Domain Module.
Covers system reminders, notifications, and immutable administrative audit logs.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Reminder Schemas
# ---------------------------------------------------------------------------
class ReminderBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    application_id: str | None = None
    remind_at: datetime
    message: str = Field(..., min_length=1)
    is_sent: bool = False


class ReminderCreate(ReminderBase):
    id: str | None = None


class ReminderUpdate(BaseModel):
    remind_at: datetime | None = None
    message: str | None = None
    is_sent: bool | None = None


class ReminderRead(ReminderBase):
    id: str
    sent_at: datetime | None = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Notification Schemas
# ---------------------------------------------------------------------------
class NotificationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    title: str = Field(..., min_length=1, max_length=255)
    content: str
    is_read: bool = False
    link: str | None = None


class NotificationCreate(NotificationBase):
    id: str | None = None


class NotificationUpdate(BaseModel):
    is_read: bool | None = None


class NotificationRead(NotificationBase):
    id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Audit Log Schemas (Immutable records)
# ---------------------------------------------------------------------------
class AuditLogBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    actor_id: str
    action: str = Field(..., min_length=1, max_length=100)
    entity_type: str = Field(..., min_length=1, max_length=100)
    entity_id: str
    details: dict[str, Any] = Field(default_factory=dict)


class AuditLogCreate(AuditLogBase):
    id: str | None = None


class AuditLogRead(AuditLogBase):
    id: str
    created_at: datetime

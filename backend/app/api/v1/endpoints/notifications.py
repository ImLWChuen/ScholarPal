from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_student
from app.domain.audit_notifications.models import Notification
from app.domain.audit_notifications.schemas import (
    NotificationCreate,
    NotificationRead,
    NotificationUpdate,
)
from app.domain.profile_preparation.models import User
from app.repositories import notification_repository

router = APIRouter()


@router.get("", response_model=list[NotificationRead])
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List notifications strictly scoped to current student."""
    return await notification_repository.list_scoped(
        db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.post("", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notif_in: NotificationCreate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new notification for the current student."""
    notif_obj = Notification(
        id=notif_in.id or f"notif_{uuid.uuid4().hex[:12]}",
        user_id=current_user.id,
        title=notif_in.title,
        content=notif_in.content,
        is_read=notif_in.is_read,
        reference_url=notif_in.link,
    )
    return await notification_repository.create(db, notif_obj)


@router.get("/{id}", response_model=NotificationRead)
async def get_notification_by_id(
    id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve notification by ID scoped to current student.
    Returns 404 if notification does not exist or belongs to another student.
    """
    notif = await notification_repository.get_by_id_scoped(db, id=id, user_id=current_user.id)
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return notif


@router.put("/{id}", response_model=NotificationRead)
@router.patch("/{id}", response_model=NotificationRead)
async def update_notification(
    id: str,
    notif_in: NotificationUpdate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update notification by ID scoped to current student.
    Returns 404 if notification does not exist or belongs to another student.
    """
    updated = await notification_repository.update_scoped(
        db, id=id, user_id=current_user.id, update_data=notif_in
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return updated


@router.delete("/{id}")
async def delete_notification(
    id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete notification by ID scoped to current student.
    Returns 404 if notification does not exist or belongs to another student.
    """
    deleted = await notification_repository.delete_scoped(db, id=id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return {"message": "Notification deleted successfully"}

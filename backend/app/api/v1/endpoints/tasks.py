from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_student
from app.domain.applications_interviews.models import ApplicationTask
from app.domain.applications_interviews.schemas import (
    ApplicationTaskCreate,
    ApplicationTaskRead,
    ApplicationTaskUpdate,
)
from app.domain.profile_preparation.models import User
from app.repositories import application_repository, task_repository

router = APIRouter()


@router.get("", response_model=list[ApplicationTaskRead])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List tasks strictly scoped to current student's applications."""
    return await task_repository.list_scoped(db, user_id=current_user.id, skip=skip, limit=limit)


@router.post("", response_model=ApplicationTaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: ApplicationTaskCreate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new task for an application owned by the current student.
    Returns 404 if application does not exist or belongs to another student.
    """
    app_obj = await application_repository.get_by_id_scoped(
        db, id=task_in.application_id, user_id=current_user.id
    )
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    task_obj = ApplicationTask(
        id=task_in.id or f"task_{uuid.uuid4().hex[:12]}",
        application_id=task_in.application_id,
        title=task_in.title,
        description=task_in.description,
        task_key=task_in.task_key or f"task_{uuid.uuid4().hex[:8]}",
        is_completed=task_in.is_completed,
        due_date=task_in.due_date,
    )
    return await task_repository.create(db, task_obj)


@router.get("/{id}", response_model=ApplicationTaskRead)
async def get_task_by_id(
    id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve task by ID scoped to current student.
    Returns 404 if task does not exist or belongs to another student.
    """
    task = await task_repository.get_by_id_scoped(db, id=id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.put("/{id}", response_model=ApplicationTaskRead)
@router.patch("/{id}", response_model=ApplicationTaskRead)
async def update_task(
    id: str,
    task_in: ApplicationTaskUpdate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update task by ID scoped to current student.
    Returns 404 if task does not exist or belongs to another student.
    """
    updated = await task_repository.update_scoped(
        db, id=id, user_id=current_user.id, update_data=task_in
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return updated


@router.delete("/{id}")
async def delete_task(
    id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete task by ID scoped to current student.
    Returns 404 if task does not exist or belongs to another student.
    """
    deleted = await task_repository.delete_scoped(db, id=id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return {"message": "Task deleted successfully"}


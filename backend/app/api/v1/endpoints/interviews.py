from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_student
from app.domain.applications_interviews.models import Interview
from app.domain.applications_interviews.schemas import (
    InterviewCreate,
    InterviewRead,
    InterviewUpdate,
)
from app.domain.profile_preparation.models import User
from app.repositories import application_repository, interview_repository

router = APIRouter()


@router.get("", response_model=list[InterviewRead])
async def list_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List interviews strictly scoped to current student's applications."""
    return await interview_repository.list_scoped(
        db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.post("", response_model=InterviewRead, status_code=status.HTTP_201_CREATED)
async def create_interview(
    interview_in: InterviewCreate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new interview for an application owned by the current student.
    Returns 404 if application does not exist or belongs to another student.
    """
    app_obj = await application_repository.get_by_id_scoped(
        db, id=interview_in.application_id, user_id=current_user.id
    )
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    interview_obj = Interview(
        id=interview_in.id or f"int_{uuid.uuid4().hex[:12]}",
        application_id=interview_in.application_id,
        round_name=interview_in.round_name,
        scheduled_at=interview_in.scheduled_at,
        location_or_url=interview_in.location_or_link,
        status=interview_in.status,
        feedback_or_notes=interview_in.feedback or interview_in.prep_notes,
    )
    return await interview_repository.create(db, interview_obj)


@router.get("/{id}", response_model=InterviewRead)
async def get_interview_by_id(
    id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve interview by ID scoped to current student.
    Returns 404 if interview does not exist or belongs to another student.
    """
    interview = await interview_repository.get_by_id_scoped(db, id=id, user_id=current_user.id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    return interview


@router.put("/{id}", response_model=InterviewRead)
@router.patch("/{id}", response_model=InterviewRead)
async def update_interview(
    id: str,
    interview_in: InterviewUpdate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update interview by ID scoped to current student.
    Returns 404 if interview does not exist or belongs to another student.
    """
    updated = await interview_repository.update_scoped(
        db, id=id, user_id=current_user.id, update_data=interview_in
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    return updated


@router.delete("/{id}")
async def delete_interview(
    id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete interview by ID scoped to current student.
    Returns 404 if interview does not exist or belongs to another student.
    """
    deleted = await interview_repository.delete_scoped(db, id=id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    return {"message": "Interview deleted successfully"}


from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_student
from app.domain.applications_interviews.models import Application
from app.domain.applications_interviews.schemas import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
)
from app.domain.profile_preparation.models import User
from app.repositories import application_repository

router = APIRouter()


@router.get("", response_model=list[ApplicationRead])
async def list_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List applications strictly scoped to current student."""
    return await application_repository.list_scoped(
        db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    app_in: ApplicationCreate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new application for the current student."""
    stage_val = app_in.stage.value if hasattr(app_in.stage, "value") else str(app_in.stage)
    new_app = Application(
        id=app_in.id or f"app_{uuid.uuid4().hex[:12]}",
        student_id=current_user.id,
        scholarship_id=app_in.scholarship_id,
        stage=stage_val,
        submitted_at=app_in.submitted_at,
        submission_reference=app_in.submission_reference or app_in.portal_submission_reference,
        notes=app_in.notes,
    )
    return await application_repository.create(db, new_app)


@router.get("/{id}", response_model=ApplicationRead)
async def get_application_by_id(
    id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve application by ID scoped to current student.
    Returns 404 if application does not exist or belongs to another student.
    """
    app_obj = await application_repository.get_by_id_scoped(db, id=id, user_id=current_user.id)
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return app_obj


@router.put("/{id}", response_model=ApplicationRead)
@router.patch("/{id}", response_model=ApplicationRead)
async def update_application(
    id: str,
    app_in: ApplicationUpdate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update application by ID scoped to current student.
    Returns 404 if application does not exist or belongs to another student.
    """
    updated = await application_repository.update_scoped(
        db, id=id, user_id=current_user.id, update_data=app_in
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return updated


@router.delete("/{id}")
async def delete_application(
    id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete application by ID scoped to current student.
    Returns 404 if application does not exist or belongs to another student.
    """
    deleted = await application_repository.delete_scoped(db, id=id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return {"message": "Application deleted successfully"}

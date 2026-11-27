from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_student
from app.domain.profile_preparation.models import User
from app.domain.profile_preparation.schemas import (
    StudentProfileRead,
    StudentProfileUpdate,
)
from app.repositories import profile_repository

router = APIRouter()


@router.get("/me", response_model=StudentProfileRead)
async def get_my_profile(
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retrieve current student's own profile."""
    profile = await profile_repository.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return profile


@router.get("/{id}", response_model=StudentProfileRead)
async def get_profile_by_id(
    id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve profile by ID scoped to current student.
    Returns 404 if profile does not exist or belongs to another student.
    """
    profile = await profile_repository.get_by_id_scoped(db, id=id, user_id=current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return profile


@router.put("/{id}", response_model=StudentProfileRead)
@router.patch("/{id}", response_model=StudentProfileRead)
async def update_profile(
    id: str,
    profile_in: StudentProfileUpdate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update profile by ID scoped to current student.
    Returns 404 if profile does not exist or belongs to another student.
    """
    updated = await profile_repository.update_scoped(
        db, id=id, user_id=current_user.id, update_data=profile_in
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return updated


@router.delete("/{id}")
async def delete_profile(
    id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete profile by ID scoped to current student.
    Returns 404 if profile does not exist or belongs to another student.
    """
    deleted = await profile_repository.delete_scoped(db, id=id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return {"message": "Profile deleted successfully"}


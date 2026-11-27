from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_student
from app.core.rate_limiter import get_client_ip
from app.domain.profile_preparation.models import StudentProfile, User
from app.domain.profile_preparation.schemas import (
    StudentProfileCreateRequest,
    StudentProfileRead,
    StudentProfileUpdate,
)
from app.repositories import profile_repository
from app.repositories.audit_repository import audit_log_repository

router = APIRouter()

PROFILE_AUDIT_FIELDS = (
    "study_level",
    "education_level",
    "nationality",
    "citizenship",
    "state_of_origin",
    "field_of_study",
    "intended_field",
    "academic_results",
    "household_income",
    "cgpa",
)


def _snapshot_profile(profile: StudentProfile) -> dict[str, Any]:
    return {field: getattr(profile, field) for field in PROFILE_AUDIT_FIELDS}


@router.post("", response_model=StudentProfileRead, status_code=status.HTTP_201_CREATED)
async def create_my_profile(
    request: Request,
    profile_in: StudentProfileCreateRequest,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a reusable student profile for the authenticated student and log the creation."""
    existing = await profile_repository.get_by_user_id(db, user_id=current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists for this student",
        )

    data = profile_in.model_dump(exclude_unset=True)
    profile = StudentProfile(
        id=data.pop("id", None) or f"prof_{uuid.uuid4().hex[:12]}",
        user_id=current_user.id,
        **data,
    )
    created = await profile_repository.create(db, profile)
    await audit_log_repository.record_event(
        db,
        actor_id=current_user.id,
        action="profile_created",
        entity_type="student_profile",
        entity_id=created.id,
        changes={"after": _snapshot_profile(created)},
        ip_address=get_client_ip(request),
    )
    return created


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


@router.put("/me", response_model=StudentProfileRead)
@router.patch("/me", response_model=StudentProfileRead)
async def update_my_profile(
    request: Request,
    profile_in: StudentProfileUpdate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update current student's own profile and record an audit log entry."""
    existing = await profile_repository.get_by_user_id(db, user_id=current_user.id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    before = _snapshot_profile(existing)
    updated = await profile_repository.update_scoped(
        db, id=existing.id, user_id=current_user.id, update_data=profile_in
    )
    assert updated is not None
    await audit_log_repository.record_event(
        db,
        actor_id=current_user.id,
        action="profile_updated",
        entity_type="student_profile",
        entity_id=updated.id,
        changes={"before": before, "after": _snapshot_profile(updated)},
        ip_address=get_client_ip(request),
    )
    return updated


@router.delete("/me")
async def delete_my_profile(
    request: Request,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Delete current student's own profile and record an audit log entry."""
    existing = await profile_repository.get_by_user_id(db, user_id=current_user.id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    before = _snapshot_profile(existing)
    profile_id = existing.id
    await profile_repository.delete_scoped(db, id=profile_id, user_id=current_user.id)
    await audit_log_repository.record_event(
        db,
        actor_id=current_user.id,
        action="profile_deleted",
        entity_type="student_profile",
        entity_id=profile_id,
        changes={"before": before},
        ip_address=get_client_ip(request),
    )
    return {"message": "Profile deleted successfully"}


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
    request: Request,
    id: str,
    profile_in: StudentProfileUpdate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update profile by ID scoped to current student and record an audit log entry.
    Returns 404 if profile does not exist or belongs to another student.
    """
    existing = await profile_repository.get_by_id_scoped(db, id=id, user_id=current_user.id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    before = _snapshot_profile(existing)
    updated = await profile_repository.update_scoped(
        db, id=id, user_id=current_user.id, update_data=profile_in
    )
    assert updated is not None
    await audit_log_repository.record_event(
        db,
        actor_id=current_user.id,
        action="profile_updated",
        entity_type="student_profile",
        entity_id=updated.id,
        changes={"before": before, "after": _snapshot_profile(updated)},
        ip_address=get_client_ip(request),
    )
    return updated


@router.delete("/{id}")
async def delete_profile(
    request: Request,
    id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete profile by ID scoped to current student and record an audit log entry.
    Returns 404 if profile does not exist or belongs to another student.
    """
    existing = await profile_repository.get_by_id_scoped(db, id=id, user_id=current_user.id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    before = _snapshot_profile(existing)
    deleted = await profile_repository.delete_scoped(db, id=id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    await audit_log_repository.record_event(
        db,
        actor_id=current_user.id,
        action="profile_deleted",
        entity_type="student_profile",
        entity_id=id,
        changes={"before": before},
        ip_address=get_client_ip(request),
    )
    return {"message": "Profile deleted successfully"}

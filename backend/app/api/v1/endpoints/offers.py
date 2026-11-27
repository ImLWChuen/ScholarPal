from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_student
from app.domain.applications_interviews.models import AwardOffer
from app.domain.applications_interviews.schemas import (
    AwardOfferCreate,
    AwardOfferRead,
    AwardOfferUpdate,
)
from app.domain.profile_preparation.models import User
from app.repositories import application_repository, offer_repository

router = APIRouter()


@router.get("", response_model=list[AwardOfferRead])
async def list_offers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List award offers strictly scoped to current student's applications."""
    return await offer_repository.list_scoped(db, user_id=current_user.id, skip=skip, limit=limit)


@router.post("", response_model=AwardOfferRead, status_code=status.HTTP_201_CREATED)
async def create_offer(
    offer_in: AwardOfferCreate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new award offer for an application owned by the current student.
    Returns 404 if application does not exist or belongs to another student.
    """
    app_obj = await application_repository.get_by_id_scoped(
        db, id=offer_in.application_id, user_id=current_user.id
    )
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    offer_obj = AwardOffer(
        id=offer_in.id or f"off_{uuid.uuid4().hex[:12]}",
        application_id=offer_in.application_id,
        offer_amount=offer_in.offer_amount,
        currency=offer_in.currency,
        bond_duration_years=offer_in.bond_duration_years,
        decision=offer_in.decision,
        response_deadline=offer_in.decision_deadline,
    )
    return await offer_repository.create(db, offer_obj)


@router.get("/{id}", response_model=AwardOfferRead)
async def get_offer_by_id(
    id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve award offer by ID scoped to current student.
    Returns 404 if offer does not exist or belongs to another student.
    """
    offer = await offer_repository.get_by_id_scoped(db, id=id, user_id=current_user.id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found",
        )
    return offer


@router.put("/{id}", response_model=AwardOfferRead)
@router.patch("/{id}", response_model=AwardOfferRead)
async def update_offer(
    id: str,
    offer_in: AwardOfferUpdate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update award offer by ID scoped to current student.
    Returns 404 if offer does not exist or belongs to another student.
    """
    updated = await offer_repository.update_scoped(
        db, id=id, user_id=current_user.id, update_data=offer_in
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found",
        )
    return updated


@router.delete("/{id}")
async def delete_offer(
    id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete award offer by ID scoped to current student.
    Returns 404 if offer does not exist or belongs to another student.
    """
    deleted = await offer_repository.delete_scoped(db, id=id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found",
        )
    return {"message": "Offer deleted successfully"}

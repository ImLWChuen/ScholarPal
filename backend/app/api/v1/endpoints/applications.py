from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_student
from app.domain.applications_interviews.models import Application, DocumentChecklistItem
from app.domain.applications_interviews.schemas import (
    ApplicationChecklistRead,
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
    DocumentChecklistItemCreateRequest,
    DocumentChecklistItemRead,
    DocumentChecklistItemUpdate,
    DocumentReadinessRead,
)
from app.domain.extraction_review.models import RequiredDocument
from app.domain.profile_preparation.models import User
from app.domain.scholarship_discovery.models import ScholarshipVersion, VersionStatus
from app.repositories import application_repository, checklist_repository
from app.services.readiness import calculate_document_readiness

router = APIRouter()


async def _get_known_required_document_ids(
    db: AsyncSession, scholarship_id: str
) -> list[str] | None:
    """
    Return the list of RequiredDocument IDs from the latest approved version of the scholarship,
    or None if no approved version exists (meaning the required document list is unknown).
    """
    version_stmt = (
        select(ScholarshipVersion.id)
        .where(
            ScholarshipVersion.scholarship_id == scholarship_id,
            ScholarshipVersion.status == VersionStatus.APPROVED.value,
        )
        .order_by(
            ScholarshipVersion.version_number.desc(),
            ScholarshipVersion.created_at.desc(),
        )
        .limit(1)
    )
    version_id = (await db.execute(version_stmt)).scalar_one_or_none()
    if version_id is None:
        return None

    docs_stmt = select(RequiredDocument.id).where(
        RequiredDocument.scholarship_version_id == version_id
    )
    return list((await db.execute(docs_stmt)).scalars().all())


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
    created = await application_repository.create(db, new_app)

    # Seed initial not-ready checklist items for any known required documents
    required_doc_ids = await _get_known_required_document_ids(db, created.scholarship_id)
    if required_doc_ids:
        for doc_id in required_doc_ids:
            slot = DocumentChecklistItem(
                id=f"chk_{uuid.uuid4().hex[:12]}",
                application_id=created.id,
                required_document_id=doc_id,
                is_verified=False,
            )
            db.add(slot)
        await db.commit()

    return created


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


@router.get("/{application_id}/readiness", response_model=DocumentReadinessRead)
async def get_application_readiness(
    application_id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Calculate document readiness for a saved application scoped to the current student.
    Returns not_available when known required documents are unknown or empty.
    """
    app_obj = await application_repository.get_by_id_scoped(
        db, id=application_id, user_id=current_user.id
    )
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    required_doc_ids = await _get_known_required_document_ids(db, app_obj.scholarship_id)
    items = await checklist_repository.list_by_application_scoped(
        db, application_id=application_id, user_id=current_user.id
    )
    return calculate_document_readiness(required_doc_ids, items)


@router.get("/{application_id}/checklist", response_model=ApplicationChecklistRead)
async def get_application_checklist(
    application_id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List checklist items and document readiness for a saved application."""
    app_obj = await application_repository.get_by_id_scoped(
        db, id=application_id, user_id=current_user.id
    )
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    required_doc_ids = await _get_known_required_document_ids(db, app_obj.scholarship_id)
    items = await checklist_repository.list_by_application_scoped(
        db, application_id=application_id, user_id=current_user.id
    )
    readiness = calculate_document_readiness(required_doc_ids, items)
    return ApplicationChecklistRead(
        application_id=application_id,
        readiness=readiness,
        items=items,
    )


@router.post(
    "/{application_id}/checklist",
    response_model=DocumentChecklistItemRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_checklist_item(
    application_id: str,
    item_in: DocumentChecklistItemCreateRequest,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Add a document checklist item with ready/not-ready flag to a saved application.
    Returns 404 if application does not belong to current student.
    """
    app_obj = await application_repository.get_by_id_scoped(
        db, id=application_id, user_id=current_user.id
    )
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # Verify required_document belongs to this application's scholarship
    doc_stmt = (
        select(RequiredDocument.id)
        .join(
            ScholarshipVersion,
            ScholarshipVersion.id == RequiredDocument.scholarship_version_id,
        )
        .where(
            RequiredDocument.id == item_in.required_document_id,
            ScholarshipVersion.scholarship_id == app_obj.scholarship_id,
        )
    )
    if (await db.execute(doc_stmt)).scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Required document does not belong to the application's scholarship",
        )

    existing_stmt = select(DocumentChecklistItem.id).where(
        DocumentChecklistItem.application_id == application_id,
        DocumentChecklistItem.required_document_id == item_in.required_document_id,
    )
    if (await db.execute(existing_stmt)).scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Checklist item for this required document already exists",
        )

    item = DocumentChecklistItem(
        id=item_in.id or f"chk_{uuid.uuid4().hex[:12]}",
        application_id=application_id,
        required_document_id=item_in.required_document_id,
        file_path=item_in.file_path,
        file_name=item_in.file_name,
        is_verified=item_in.is_ready,
        notes=item_in.notes,
    )
    return await checklist_repository.create(db, item)


@router.put("/{application_id}/checklist/{item_id}", response_model=DocumentChecklistItemRead)
@router.patch("/{application_id}/checklist/{item_id}", response_model=DocumentChecklistItemRead)
async def update_checklist_item(
    application_id: str,
    item_id: str,
    item_in: DocumentChecklistItemUpdate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update ready/not-ready flag or file metadata on a checklist item."""
    existing = await checklist_repository.get_by_app_and_id_scoped(
        db, application_id=application_id, item_id=item_id, user_id=current_user.id
    )
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist item not found",
        )
    updated = await checklist_repository.update_scoped(
        db, id=item_id, user_id=current_user.id, update_data=item_in
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist item not found",
        )
    return updated


@router.delete("/{application_id}/checklist/{item_id}")
async def delete_checklist_item(
    application_id: str,
    item_id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Delete a checklist item from a saved application."""
    existing = await checklist_repository.get_by_app_and_id_scoped(
        db, application_id=application_id, item_id=item_id, user_id=current_user.id
    )
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist item not found",
        )
    await checklist_repository.delete_scoped(db, id=item_id, user_id=current_user.id)
    return {"message": "Checklist item deleted successfully"}

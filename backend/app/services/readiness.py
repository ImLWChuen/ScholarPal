from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from app.domain.applications_interviews.schemas import DocumentReadinessRead


def calculate_document_readiness(
    required_document_ids: Sequence[str] | None,
    checklist_items: Sequence[Any],
) -> DocumentReadinessRead:
    """
    Calculate document readiness percentage:
        (ready_items / total_known_required_documents) * 100

    Returns status='not_available' and readiness_percentage=None when the
    required documents list is unknown (None) or empty.
    """
    if not required_document_ids:
        return DocumentReadinessRead(
            ready_count=0,
            total_required=0 if required_document_ids is not None else None,
            readiness_percentage=None,
            status="not_available",
            display="Not available",
        )

    required_set = set(required_document_ids)
    total_required = len(required_set)
    ready_doc_ids = {
        item.required_document_id
        for item in checklist_items
        if getattr(item, "is_ready", getattr(item, "is_verified", False))
        and item.required_document_id in required_set
    }
    ready_count = len(ready_doc_ids)
    percentage = round((ready_count / total_required) * 100, 2)

    if ready_count == total_required:
        status_str = "complete"
    elif ready_count > 0:
        status_str = "partial"
    else:
        status_str = "not_started"

    return DocumentReadinessRead(
        ready_count=ready_count,
        total_required=total_required,
        readiness_percentage=percentage,
        status=status_str,
        display=f"{percentage:.2f}%",
    )

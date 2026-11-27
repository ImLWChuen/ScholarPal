"""
Tests for Reusable Student Profile CRUD with Audit Logging,
Document Checklist Items per Saved Application, and Document Readiness Calculation.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.security import create_access_token
from app.domain.audit_notifications.models import AuditLog
from app.domain.extraction_review.models import RequiredDocument
from app.domain.profile_preparation.models import User
from app.domain.scholarship_discovery.models import (
    Scholarship,
    ScholarshipVersion,
    VersionStatus,
)
from app.domain.shared_enums import UserRole
from app.services.readiness import calculate_document_readiness


# ---------------------------------------------------------------------------
# 1. Pure Unit Tests for Document Readiness Calculation
# ---------------------------------------------------------------------------
def test_readiness_unknown_required_documents_returns_not_available() -> None:
    result = calculate_document_readiness(None, [])
    assert result.status == "not_available"
    assert result.readiness_percentage is None
    assert result.total_required is None
    assert result.ready_count == 0
    assert result.display == "Not available"


def test_readiness_empty_required_documents_returns_not_available() -> None:
    result = calculate_document_readiness([], [])
    assert result.status == "not_available"
    assert result.readiness_percentage is None
    assert result.total_required == 0
    assert result.ready_count == 0
    assert result.display == "Not available"


def test_readiness_partial_list() -> None:
    required_ids = ["doc-1", "doc-2", "doc-3"]
    items = [
        SimpleNamespace(required_document_id="doc-1", is_ready=True),
        SimpleNamespace(required_document_id="doc-2", is_ready=False),
        SimpleNamespace(required_document_id="doc-3", is_ready=False),
    ]
    result = calculate_document_readiness(required_ids, items)
    assert result.status == "partial"
    assert result.ready_count == 1
    assert result.total_required == 3
    assert result.readiness_percentage == 33.33
    assert result.display == "33.33%"


def test_readiness_not_started_list() -> None:
    required_ids = ["doc-1", "doc-2"]
    items = [
        SimpleNamespace(required_document_id="doc-1", is_ready=False),
        SimpleNamespace(required_document_id="doc-2", is_ready=False),
    ]
    result = calculate_document_readiness(required_ids, items)
    assert result.status == "not_started"
    assert result.ready_count == 0
    assert result.total_required == 2
    assert result.readiness_percentage == 0.0
    assert result.display == "0.00%"


def test_readiness_complete_list() -> None:
    required_ids = ["doc-1", "doc-2", "doc-3"]
    items = [
        SimpleNamespace(required_document_id="doc-1", is_ready=True),
        SimpleNamespace(required_document_id="doc-2", is_ready=True),
        SimpleNamespace(required_document_id="doc-3", is_ready=True),
    ]
    result = calculate_document_readiness(required_ids, items)
    assert result.status == "complete"
    assert result.ready_count == 3
    assert result.total_required == 3
    assert result.readiness_percentage == 100.0
    assert result.display == "100.00%"


# ---------------------------------------------------------------------------
# 2. Student Profile CRUD + Validation + Audit Log Tests
# ---------------------------------------------------------------------------
@pytest.fixture
async def seeded_student(async_db: async_sessionmaker[AsyncSession]) -> dict[str, str]:
    async with async_db() as session:
        user_a = User(
            id="usr-prof-a",
            email="profile.a@example.com",
            full_name="Profile Student A",
            role=UserRole.STUDENT.value,
            is_active=True,
        )
        user_b = User(
            id="usr-prof-b",
            email="profile.b@example.com",
            full_name="Profile Student B",
            role=UserRole.STUDENT.value,
            is_active=True,
        )
        session.add_all([user_a, user_b])
        await session.commit()

    return {
        "user_a_id": "usr-prof-a",
        "user_b_id": "usr-prof-b",
        "token_a": create_access_token("usr-prof-a", role="student"),
        "token_b": create_access_token("usr-prof-b", role="student"),
    }


async def test_profile_crud_lifecycle_with_audit_logs(
    async_client: AsyncClient,
    async_db: async_sessionmaker[AsyncSession],
    seeded_student: dict[str, str],
) -> None:
    headers = {"Authorization": f"Bearer {seeded_student['token_a']}"}

    # 1. Create profile (Rule 5: household_income omitted stays None)
    create_payload = {
        "study_level": "Undergraduate",
        "citizenship": "Malaysian",
        "state_of_origin": "Penang",
        "cgpa": 3.75,
        "academic_results": {"SPM": {"BM": "A+", "Math": "A"}},
    }
    resp_create = await async_client.post("/api/v1/profiles", json=create_payload, headers=headers)
    assert resp_create.status_code == 201
    created = resp_create.json()
    profile_id = created["id"]
    assert created["user_id"] == seeded_student["user_a_id"]
    assert created["household_income"] is None
    assert created["cgpa"] == 3.75

    # Duplicate create must be rejected (409)
    resp_dup = await async_client.post("/api/v1/profiles", json=create_payload, headers=headers)
    assert resp_dup.status_code == 409

    # 2. Read via /me and /{id}
    resp_me = await async_client.get("/api/v1/profiles/me", headers=headers)
    assert resp_me.status_code == 200
    assert resp_me.json()["id"] == profile_id

    # 3. Update via PATCH /me
    resp_update = await async_client.patch(
        "/api/v1/profiles/me",
        json={"cgpa": 3.9, "household_income": 4500.0},
        headers=headers,
    )
    assert resp_update.status_code == 200
    assert resp_update.json()["cgpa"] == 3.9
    assert resp_update.json()["household_income"] == 4500.0

    # 4. Delete via DELETE /me
    resp_delete = await async_client.delete("/api/v1/profiles/me", headers=headers)
    assert resp_delete.status_code == 200

    resp_after_del = await async_client.get("/api/v1/profiles/me", headers=headers)
    assert resp_after_del.status_code == 404

    # 5. Verify AuditLog entries were recorded for create, update, and delete
    async with async_db() as session:
        logs = list(
            (
                await session.execute(
                    select(AuditLog)
                    .where(AuditLog.entity_id == profile_id)
                    .order_by(AuditLog.timestamp.asc())
                )
            )
            .scalars()
            .all()
        )
    actions = [log.action for log in logs]
    assert actions == ["profile_created", "profile_updated", "profile_deleted"]
    assert all(log.actor_id == seeded_student["user_a_id"] for log in logs)
    assert logs[1].changes["before"]["cgpa"] == 3.75
    assert logs[1].changes["after"]["cgpa"] == 3.9


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {"cgpa": 4.5},
        {"cgpa": -0.1},
        {"household_income": -100.0},
        {"study_level": "InvalidDegreeLevel"},
        {"academic_results": {"BM": "Z99"}},
    ],
)
async def test_profile_server_side_validation_rejects_invalid_inputs(
    async_client: AsyncClient,
    seeded_student: dict[str, str],
    invalid_payload: dict[str, object],
) -> None:
    headers = {"Authorization": f"Bearer {seeded_student['token_a']}"}
    resp = await async_client.post("/api/v1/profiles", json=invalid_payload, headers=headers)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 3. Checklist & Readiness API Integration Tests
# ---------------------------------------------------------------------------
@pytest.fixture
async def seeded_scholarships(async_db: async_sessionmaker[AsyncSession]) -> dict[str, str]:
    async with async_db() as session:
        # Scholarship 1: Approved version with 3 required documents
        sch_full = Scholarship(
            id="sch-chk-full",
            title="Full Checklist Scholarship",
            provider="Yayasan Full",
            official_portal_url="https://full.example.org",
        )
        ver_full = ScholarshipVersion(
            id="ver-chk-full",
            scholarship_id="sch-chk-full",
            application_cycle="2026",
            version_number=1,
            title="Full Checklist Scholarship 2026",
            status=VersionStatus.APPROVED.value,
        )
        docs_full = [
            RequiredDocument(
                id="req-doc-1",
                scholarship_version_id="ver-chk-full",
                name="Academic Transcript",
            ),
            RequiredDocument(
                id="req-doc-2",
                scholarship_version_id="ver-chk-full",
                name="NRIC Copy",
            ),
            RequiredDocument(
                id="req-doc-3",
                scholarship_version_id="ver-chk-full",
                name="Income Statement",
            ),
        ]

        # Scholarship 2: Approved version with 0 required documents (empty)
        sch_empty = Scholarship(
            id="sch-chk-empty",
            title="Empty Docs Scholarship",
            provider="Yayasan Empty",
            official_portal_url="https://empty.example.org",
        )
        ver_empty = ScholarshipVersion(
            id="ver-chk-empty",
            scholarship_id="sch-chk-empty",
            application_cycle="2026",
            version_number=1,
            title="Empty Docs Scholarship 2026",
            status=VersionStatus.APPROVED.value,
        )

        # Scholarship 3: No approved version (unknown)
        sch_unknown = Scholarship(
            id="sch-chk-unknown",
            title="Unknown Docs Scholarship",
            provider="Yayasan Unknown",
            official_portal_url="https://unknown.example.org",
        )

        session.add_all([sch_full, ver_full, *docs_full, sch_empty, ver_empty, sch_unknown])
        await session.commit()

    return {
        "full": "sch-chk-full",
        "empty": "sch-chk-empty",
        "unknown": "sch-chk-unknown",
    }


async def test_application_checklist_and_readiness_flow(
    async_client: AsyncClient,
    seeded_student: dict[str, str],
    seeded_scholarships: dict[str, str],
) -> None:
    headers_a = {"Authorization": f"Bearer {seeded_student['token_a']}"}
    headers_b = {"Authorization": f"Bearer {seeded_student['token_b']}"}

    # 1. Unknown required documents -> not_available
    resp_app_unk = await async_client.post(
        "/api/v1/applications",
        json={
            "student_id": seeded_student["user_a_id"],
            "scholarship_id": seeded_scholarships["unknown"],
        },
        headers=headers_a,
    )
    assert resp_app_unk.status_code == 201
    app_unk_id = resp_app_unk.json()["id"]
    resp_read_unk = await async_client.get(
        f"/api/v1/applications/{app_unk_id}/readiness", headers=headers_a
    )
    assert resp_read_unk.status_code == 200
    assert resp_read_unk.json()["status"] == "not_available"
    assert resp_read_unk.json()["readiness_percentage"] is None

    # 2. Empty required documents -> not_available
    resp_app_emp = await async_client.post(
        "/api/v1/applications",
        json={
            "student_id": seeded_student["user_a_id"],
            "scholarship_id": seeded_scholarships["empty"],
        },
        headers=headers_a,
    )
    assert resp_app_emp.status_code == 201
    app_emp_id = resp_app_emp.json()["id"]
    resp_read_emp = await async_client.get(
        f"/api/v1/applications/{app_emp_id}/readiness", headers=headers_a
    )
    assert resp_read_emp.status_code == 200
    assert resp_read_emp.json()["status"] == "not_available"
    assert resp_read_emp.json()["readiness_percentage"] is None

    # 3. Full scholarship (3 required docs) -> auto-seeded as not_ready (0%)
    resp_app_full = await async_client.post(
        "/api/v1/applications",
        json={
            "student_id": seeded_student["user_a_id"],
            "scholarship_id": seeded_scholarships["full"],
        },
        headers=headers_a,
    )
    assert resp_app_full.status_code == 201
    app_full_id = resp_app_full.json()["id"]

    resp_chk = await async_client.get(
        f"/api/v1/applications/{app_full_id}/checklist", headers=headers_a
    )
    assert resp_chk.status_code == 200
    data = resp_chk.json()
    assert len(data["items"]) == 3
    assert all(item["is_ready"] is False for item in data["items"])
    assert data["readiness"]["readiness_percentage"] == 0.0
    assert data["readiness"]["status"] == "not_started"

    # Mark 1 item ready -> partial (33.33%)
    item_1_id = data["items"][0]["id"]
    resp_patch_1 = await async_client.patch(
        f"/api/v1/applications/{app_full_id}/checklist/{item_1_id}",
        json={"is_ready": True, "file_name": "transcript.pdf"},
        headers=headers_a,
    )
    assert resp_patch_1.status_code == 200
    assert resp_patch_1.json()["is_ready"] is True

    resp_read_partial = await async_client.get(
        f"/api/v1/applications/{app_full_id}/readiness", headers=headers_a
    )
    assert resp_read_partial.json()["status"] == "partial"
    assert resp_read_partial.json()["readiness_percentage"] == 33.33

    # Mark remaining 2 items ready -> complete (100%)
    for item in data["items"][1:]:
        resp_p = await async_client.patch(
            f"/api/v1/applications/{app_full_id}/checklist/{item['id']}",
            json={"is_ready": True},
            headers=headers_a,
        )
        assert resp_p.status_code == 200

    resp_read_complete = await async_client.get(
        f"/api/v1/applications/{app_full_id}/readiness", headers=headers_a
    )
    assert resp_read_complete.json()["status"] == "complete"
    assert resp_read_complete.json()["readiness_percentage"] == 100.0

    # Student B accessing Student A's checklist or readiness -> 404
    assert (
        await async_client.get(f"/api/v1/applications/{app_full_id}/checklist", headers=headers_b)
    ).status_code == 404
    assert (
        await async_client.get(f"/api/v1/applications/{app_full_id}/readiness", headers=headers_b)
    ).status_code == 404
    assert (
        await async_client.patch(
            f"/api/v1/applications/{app_full_id}/checklist/{item_1_id}",
            json={"is_ready": False},
            headers=headers_b,
        )
    ).status_code == 404

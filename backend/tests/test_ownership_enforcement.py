"""
Tests for Ownership Enforcement in the Repository and API Layer.

Non-negotiable rule 8: Strict data segregation by student_id / user_id.
All queries for profiles, applications, tasks, interviews, offers, and notifications
must be scoped to the authenticated user ID.
Accessing or attempting to mutate another student's record must return HTTP 404 (NOT 403)
to prevent resource enumeration.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.security import create_access_token
from app.domain.applications_interviews.models import (
    Application,
    ApplicationStage,
    ApplicationTask,
    AwardOffer,
    Interview,
)
from app.domain.audit_notifications.models import Notification
from app.domain.profile_preparation.models import StudentProfile, User
from app.domain.scholarship_discovery.models import Scholarship
from app.domain.shared_enums import UserRole
from app.repositories import (
    application_repository,
    interview_repository,
    notification_repository,
    offer_repository,
    profile_repository,
    task_repository,
)

STUDENT_A_ID = "usr-student-a"
STUDENT_B_ID = "usr-student-b"
SCHOLARSHIP_ID = "sch-test-ownership-1"

STUDENT_A_RECORDS = {
    "profile": "prof-student-a",
    "application": "app-student-a",
    "task": "task-student-a",
    "interview": "int-student-a",
    "offer": "off-student-a",
    "notification": "notif-student-a",
}

STUDENT_B_RECORDS = {
    "profile": "prof-student-b",
    "application": "app-student-b",
    "task": "task-student-b",
    "interview": "int-student-b",
    "offer": "off-student-b",
    "notification": "notif-student-b",
}


@pytest.fixture
async def seed_ownership_data(async_db: async_sessionmaker[AsyncSession]):
    """Seed two students with isolated records across all 6 scoped entities."""
    now = datetime.now(UTC)

    async with async_db() as session:
        # 1. Users
        student_a = User(
            id=STUDENT_A_ID,
            email="student.a@example.com",
            full_name="Student A",
            role=UserRole.STUDENT.value,
            is_active=True,
        )
        student_b = User(
            id=STUDENT_B_ID,
            email="student.b@example.com",
            full_name="Student B",
            role=UserRole.STUDENT.value,
            is_active=True,
        )
        session.add_all([student_a, student_b])

        # 2. Shared Scholarship
        scholarship = Scholarship(
            id=SCHOLARSHIP_ID,
            title="Yayasan Test Scholarship",
            provider="Yayasan Test",
            official_portal_url="https://scholarship.test.org",
        )
        session.add(scholarship)
        await session.flush()

        # 3. Student A Records
        prof_a = StudentProfile(
            id=STUDENT_A_RECORDS["profile"],
            user_id=STUDENT_A_ID,
            study_level="Undergraduate",
            citizenship="Malaysian",
            state_of_origin="Selangor",
            cgpa=3.85,
            household_income=5000.0,
        )
        app_a = Application(
            id=STUDENT_A_RECORDS["application"],
            student_id=STUDENT_A_ID,
            scholarship_id=SCHOLARSHIP_ID,
            stage=ApplicationStage.PREPARING.value,
            notes="Student A Private Notes",
        )
        session.add_all([prof_a, app_a])
        await session.flush()

        task_a = ApplicationTask(
            id=STUDENT_A_RECORDS["task"],
            application_id=app_a.id,
            title="Personal Statement Draft",
            task_key="key_task_a_1",
            is_completed=False,
        )
        int_a = Interview(
            id=STUDENT_A_RECORDS["interview"],
            application_id=app_a.id,
            round_name="Student A Round 1",
            scheduled_at=now,
            status="scheduled",
        )
        off_a = AwardOffer(
            id=STUDENT_A_RECORDS["offer"],
            application_id=app_a.id,
            offer_amount=75000.0,
            currency="MYR",
            decision="pending",
        )
        notif_a = Notification(
            id=STUDENT_A_RECORDS["notification"],
            user_id=STUDENT_A_ID,
            title="Student A Alert",
            content="Your application is in preparing stage.",
        )
        session.add_all([task_a, int_a, off_a, notif_a])

        # 4. Student B Records
        prof_b = StudentProfile(
            id=STUDENT_B_RECORDS["profile"],
            user_id=STUDENT_B_ID,
            study_level="Postgraduate",
            citizenship="Malaysian",
            state_of_origin="Penang",
            cgpa=3.60,
            household_income=9000.0,
        )
        app_b = Application(
            id=STUDENT_B_RECORDS["application"],
            student_id=STUDENT_B_ID,
            scholarship_id=SCHOLARSHIP_ID,
            stage=ApplicationStage.SAVED.value,
            notes="Student B Private Notes",
        )
        session.add_all([prof_b, app_b])
        await session.flush()

        task_b = ApplicationTask(
            id=STUDENT_B_RECORDS["task"],
            application_id=app_b.id,
            title="Upload Resume",
            task_key="key_task_b_1",
            is_completed=False,
        )
        int_b = Interview(
            id=STUDENT_B_RECORDS["interview"],
            application_id=app_b.id,
            round_name="Student B Screening",
            scheduled_at=now,
            status="scheduled",
        )
        off_b = AwardOffer(
            id=STUDENT_B_RECORDS["offer"],
            application_id=app_b.id,
            offer_amount=30000.0,
            currency="MYR",
            decision="pending",
        )
        notif_b = Notification(
            id=STUDENT_B_RECORDS["notification"],
            user_id=STUDENT_B_ID,
            title="Student B Alert",
            content="Welcome to ScholarPal.",
        )
        session.add_all([task_b, int_b, off_b, notif_b])
        await session.commit()

    return {
        "student_a_token": create_access_token(STUDENT_A_ID, role="student"),
        "student_b_token": create_access_token(STUDENT_B_ID, role="student"),
    }


# ---------------------------------------------------------------------------
# Parameterised Scenarios across all 6 Student Resources
# ---------------------------------------------------------------------------
STUDENT_ENDPOINT_SCENARIOS = [
    (
        "profile",
        "/api/v1/profiles",
        STUDENT_A_RECORDS["profile"],
        {"citizenship": "Singaporean", "state_of_origin": "Johor", "cgpa": 3.95},
    ),
    (
        "application",
        "/api/v1/applications",
        STUDENT_A_RECORDS["application"],
        {"stage": "Submitted", "notes": "Attacker replaced notes"},
    ),
    (
        "task",
        "/api/v1/tasks",
        STUDENT_A_RECORDS["task"],
        {"title": "Compromised Task", "is_completed": True},
    ),
    (
        "interview",
        "/api/v1/interviews",
        STUDENT_A_RECORDS["interview"],
        {"round_name": "Tampered Round", "status": "completed"},
    ),
    (
        "offer",
        "/api/v1/offers",
        STUDENT_A_RECORDS["offer"],
        {"offer_amount": 999999.0, "decision": "declined"},
    ),
    (
        "notification",
        "/api/v1/notifications",
        STUDENT_A_RECORDS["notification"],
        {"is_read": True},
    ),
]


@pytest.mark.parametrize(
    "entity_name,base_url,target_record_id,update_payload",
    STUDENT_ENDPOINT_SCENARIOS,
)
async def test_read_other_student_record_returns_404_not_403(
    async_client: AsyncClient,
    seed_ownership_data: dict[str, str],
    entity_name: str,
    base_url: str,
    target_record_id: str,
    update_payload: dict[str, Any],
) -> None:
    """
    Attempting to READ another student's record must return HTTP 404 (not 403)
    to prevent resource enumeration.
    """
    headers_b = {"Authorization": f"Bearer {seed_ownership_data['student_b_token']}"}
    headers_a = {"Authorization": f"Bearer {seed_ownership_data['student_a_token']}"}

    # Student B attempts to read Student A's record -> must return 404
    resp_b = await async_client.get(f"{base_url}/{target_record_id}", headers=headers_b)
    assert resp_b.status_code == 404, (
        f"Expected 404 for {entity_name} reading another student's record, "
        f"got {resp_b.status_code}: {resp_b.text}"
    )
    assert "not found" in resp_b.json().get("detail", "").lower()

    # Legitimate owner Student A reads the same record -> must succeed (200)
    resp_a = await async_client.get(f"{base_url}/{target_record_id}", headers=headers_a)
    assert resp_a.status_code == 200, (
        f"Owner Student A failed to read own {entity_name}: {resp_a.text}"
    )
    assert resp_a.json()["id"] == target_record_id


@pytest.mark.parametrize(
    "entity_name,base_url,target_record_id,update_payload",
    STUDENT_ENDPOINT_SCENARIOS,
)
async def test_update_other_student_record_returns_404_not_403(
    async_client: AsyncClient,
    seed_ownership_data: dict[str, str],
    entity_name: str,
    base_url: str,
    target_record_id: str,
    update_payload: dict[str, Any],
) -> None:
    """
    Attempting to UPDATE (PUT/PATCH) another student's record must return HTTP 404 (not 403).
    The underlying record must remain un-mutated.
    """
    headers_b = {"Authorization": f"Bearer {seed_ownership_data['student_b_token']}"}
    headers_a = {"Authorization": f"Bearer {seed_ownership_data['student_a_token']}"}

    # 1. Student B attempts PUT on Student A's record -> 404
    resp_b_put = await async_client.put(
        f"{base_url}/{target_record_id}", json=update_payload, headers=headers_b
    )
    assert resp_b_put.status_code == 404, (
        f"Expected 404 for PUT {entity_name} on another student's record, "
        f"got {resp_b_put.status_code}: {resp_b_put.text}"
    )

    # 2. Student B attempts PATCH on Student A's record -> 404
    resp_b_patch = await async_client.patch(
        f"{base_url}/{target_record_id}", json=update_payload, headers=headers_b
    )
    assert resp_b_patch.status_code == 404, (
        f"Expected 404 for PATCH {entity_name} on another student's record, "
        f"got {resp_b_patch.status_code}: {resp_b_patch.text}"
    )

    # 3. Verify Student A's record was NOT mutated
    resp_verify = await async_client.get(f"{base_url}/{target_record_id}", headers=headers_a)
    assert resp_verify.status_code == 200

    # 4. Legitimate owner Student A updates own record -> 200
    resp_a_put = await async_client.put(
        f"{base_url}/{target_record_id}", json=update_payload, headers=headers_a
    )
    assert resp_a_put.status_code == 200, (
        f"Owner Student A failed to update own {entity_name}: {resp_a_put.text}"
    )


@pytest.mark.parametrize(
    "entity_name,base_url,target_record_id,update_payload",
    STUDENT_ENDPOINT_SCENARIOS,
)
async def test_delete_other_student_record_returns_404_not_403(
    async_client: AsyncClient,
    seed_ownership_data: dict[str, str],
    entity_name: str,
    base_url: str,
    target_record_id: str,
    update_payload: dict[str, Any],
) -> None:
    """
    Attempting to DELETE another student's record must return HTTP 404 (not 403).
    The record must not be deleted. Owner can delete their own record.
    """
    headers_b = {"Authorization": f"Bearer {seed_ownership_data['student_b_token']}"}
    headers_a = {"Authorization": f"Bearer {seed_ownership_data['student_a_token']}"}

    # 1. Student B attempts to DELETE Student A's record -> 404
    resp_b_del = await async_client.delete(f"{base_url}/{target_record_id}", headers=headers_b)
    assert resp_b_del.status_code == 404, (
        f"Expected 404 for DELETE {entity_name} on another student's record, "
        f"got {resp_b_del.status_code}: {resp_b_del.text}"
    )

    # 2. Verify record still exists for Student A
    resp_check = await async_client.get(f"{base_url}/{target_record_id}", headers=headers_a)
    assert resp_check.status_code == 200, f"{entity_name} was deleted or compromised by Student B!"

    # 3. Legitimate owner Student A deletes own record -> 200
    resp_a_del = await async_client.delete(f"{base_url}/{target_record_id}", headers=headers_a)
    assert resp_a_del.status_code == 200

    # 4. Record is now gone for everyone -> 404
    resp_gone = await async_client.get(f"{base_url}/{target_record_id}", headers=headers_a)
    assert resp_gone.status_code == 404


# ---------------------------------------------------------------------------
# Cross-User Association Injection Prevention
# ---------------------------------------------------------------------------
async def test_cannot_inject_task_into_another_students_application(
    async_client: AsyncClient,
    seed_ownership_data: dict[str, str],
) -> None:
    """Student B cannot create a task referencing Student A's application."""
    headers_b = {"Authorization": f"Bearer {seed_ownership_data['student_b_token']}"}
    payload = {
        "application_id": STUDENT_A_RECORDS["application"],
        "title": "Malicious Injected Task",
        "task_key": "injected_task_key",
    }
    resp = await async_client.post("/api/v1/tasks", json=payload, headers=headers_b)
    assert resp.status_code == 404
    assert "not found" in resp.json().get("detail", "").lower()


async def test_cannot_inject_interview_into_another_students_application(
    async_client: AsyncClient,
    seed_ownership_data: dict[str, str],
) -> None:
    """Student B cannot create an interview referencing Student A's application."""
    headers_b = {"Authorization": f"Bearer {seed_ownership_data['student_b_token']}"}
    payload = {
        "application_id": STUDENT_A_RECORDS["application"],
        "scheduled_at": datetime.now(UTC).isoformat(),
        "round_name": "Injected Round",
    }
    resp = await async_client.post("/api/v1/interviews", json=payload, headers=headers_b)
    assert resp.status_code == 404
    assert "not found" in resp.json().get("detail", "").lower()


async def test_cannot_inject_offer_into_another_students_application(
    async_client: AsyncClient,
    seed_ownership_data: dict[str, str],
) -> None:
    """Student B cannot create an offer referencing Student A's application."""
    headers_b = {"Authorization": f"Bearer {seed_ownership_data['student_b_token']}"}
    payload = {
        "application_id": STUDENT_A_RECORDS["application"],
        "offer_amount": 100000.0,
        "currency": "MYR",
    }
    resp = await async_client.post("/api/v1/offers", json=payload, headers=headers_b)
    assert resp.status_code == 404
    assert "not found" in resp.json().get("detail", "").lower()


# ---------------------------------------------------------------------------
# List Scoping Verification
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "endpoint,expected_id,forbidden_id",
    [
        (
            "/api/v1/applications",
            STUDENT_B_RECORDS["application"],
            STUDENT_A_RECORDS["application"],
        ),
        (
            "/api/v1/tasks",
            STUDENT_B_RECORDS["task"],
            STUDENT_A_RECORDS["task"],
        ),
        (
            "/api/v1/interviews",
            STUDENT_B_RECORDS["interview"],
            STUDENT_A_RECORDS["interview"],
        ),
        (
            "/api/v1/offers",
            STUDENT_B_RECORDS["offer"],
            STUDENT_A_RECORDS["offer"],
        ),
        (
            "/api/v1/notifications",
            STUDENT_B_RECORDS["notification"],
            STUDENT_A_RECORDS["notification"],
        ),
    ],
)
async def test_list_endpoints_strictly_scoped_to_authenticated_user(
    async_client: AsyncClient,
    seed_ownership_data: dict[str, str],
    endpoint: str,
    expected_id: str,
    forbidden_id: str,
) -> None:
    """List queries must return only records belonging to authenticated user."""
    headers_b = {"Authorization": f"Bearer {seed_ownership_data['student_b_token']}"}
    resp = await async_client.get(endpoint, headers=headers_b)
    assert resp.status_code == 200

    items = resp.json()
    returned_ids = [item["id"] for item in items]
    assert expected_id in returned_ids
    assert forbidden_id not in returned_ids


# ---------------------------------------------------------------------------
# Direct Repository Layer Scoping Tests
# ---------------------------------------------------------------------------
async def test_repository_layer_ownership_scoping_isolation(
    async_db: async_sessionmaker[AsyncSession],
    seed_ownership_data: dict[str, str],
) -> None:
    """Verify repository methods directly enforce ownership scoping."""
    async with async_db() as session:
        # Profile repo
        assert (
            await profile_repository.get_by_id_scoped(
                session, STUDENT_A_RECORDS["profile"], user_id=STUDENT_B_ID
            )
            is None
        )
        assert (
            await profile_repository.verify_ownership(
                session, STUDENT_A_RECORDS["profile"], user_id=STUDENT_B_ID
            )
            is False
        )
        assert (
            await profile_repository.delete_scoped(
                session, STUDENT_A_RECORDS["profile"], user_id=STUDENT_B_ID
            )
            is False
        )

        # Application repo
        assert (
            await application_repository.get_by_id_scoped(
                session, STUDENT_A_RECORDS["application"], user_id=STUDENT_B_ID
            )
            is None
        )

        # Task repo (joined scoping)
        assert (
            await task_repository.get_by_id_scoped(
                session, STUDENT_A_RECORDS["task"], user_id=STUDENT_B_ID
            )
            is None
        )

        # Interview repo (joined scoping)
        assert (
            await interview_repository.get_by_id_scoped(
                session, STUDENT_A_RECORDS["interview"], user_id=STUDENT_B_ID
            )
            is None
        )

        # Offer repo (joined scoping)
        assert (
            await offer_repository.get_by_id_scoped(
                session, STUDENT_A_RECORDS["offer"], user_id=STUDENT_B_ID
            )
            is None
        )

        # Notification repo
        assert (
            await notification_repository.get_by_id_scoped(
                session, STUDENT_A_RECORDS["notification"], user_id=STUDENT_B_ID
            )
            is None
        )


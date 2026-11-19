"""
Seed data entry point for ScholarPal PostgreSQL database.
Populates baseline users, sources, scholarships, versions, requirements, and applications.
Includes 15 realistic fictional scholarships and 5 boundary-case student profiles,
all marked with explicit demo flags so they never appear as current opportunities.

Adheres strictly to ScholarPal Non-Negotiable Rules:
- Rule 1 & 2: Predefined rules with 3-state evaluation (satisfied, unmet, unresolved).
- Rule 4: Preserves records with 'fresh' freshness.
- Rule 5: Unknown values remain None, never zero.
- Rule 7: External provider submission portal URLs.
- Rule 8: Student ownership on student records.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.core.fixtures import (
    FIXTURE_ADMINISTRATORS,
    FIXTURE_DOCUMENTS,
    FIXTURE_REQUIREMENTS,
    FIXTURE_SCHOLARSHIP_VERSIONS,
    FIXTURE_SCHOLARSHIPS,
    FIXTURE_SOURCES,
    FIXTURE_STUDENT_PROFILES,
    FIXTURE_STUDENT_USERS,
)
from app.domain import (
    Application,
    ApplicationStage,
    ApplicationTask,
    ComparisonSet,
    EligibilityRule,
    Notification,
    RequiredDocument,
    Requirement,
    Scholarship,
    ScholarshipVersion,
    Source,
    StudentProfile,
    User,
    UserRole,
    VersionStatus,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

SAMPLE_USERS = [
    {
        "id": "student-demo-123",
        "email": "ahmad.student@scholarpal.my",
        "full_name": "Ahmad bin Abdullah",
        "role": UserRole.STUDENT.value,
        "is_active": True,
    },
    {
        "id": "admin-demo-001",
        "email": "admin.siti@scholarpal.my",
        "full_name": "Siti Aminah (Scholarship Reviewer)",
        "role": UserRole.ADMINISTRATOR.value,
        "is_active": True,
    },
]

SAMPLE_SOURCES = [
    {
        "id": "src-yayasan-khazanah",
        "name": "Yayasan Khazanah",
        "base_url": "https://www.yayasankhazanah.com.my",
        "config": {"crawl_delay": 2, "timeout": 15},
        "schedule": "0 2 * * *",
        "is_active": True,
    },
    {
        "id": "src-jpa-penajaan",
        "name": "JPA Penajaan (eSila)",
        "base_url": "https://penajaan.jpa.gov.my",
        "config": {"crawl_delay": 3, "timeout": 20},
        "schedule": "0 3 * * *",
        "is_active": True,
    },
    {
        "id": "src-bank-negara-malaysia",
        "name": "Bank Negara Malaysia",
        "base_url": "https://www.bnm.gov.my",
        "config": {"crawl_delay": 2, "timeout": 15},
        "schedule": "0 4 * * *",
        "is_active": True,
    },
    {
        "id": "src-yayasan-petronas",
        "name": "Yayasan PETRONAS",
        "base_url": "https://www.yayasanpetronas.com.my",
        "config": {"crawl_delay": 2, "timeout": 15},
        "schedule": "0 5 * * *",
        "is_active": True,
    },
]

SAMPLE_SCHOLARSHIPS = [
    {
        "id": "sch-khazanah-global-2026",
        "source_id": "src-yayasan-khazanah",
        "title": "Yayasan Khazanah Global Scholarship Programme 2026",
        "provider": "Yayasan Khazanah",
        "official_portal_url": "https://www.yayasankhazanah.com.my/scholarships/global",
        "deadline": datetime(2026, 6, 30, 23, 59, 59, tzinfo=UTC),
        "status": "open",
        "freshness": "fresh",
        "last_verified_at": datetime.now(UTC),
    },
    {
        "id": "sch-jpa-ppn-2026",
        "source_id": "src-jpa-penajaan",
        "title": "JPA Program Penajaan Nasional (PPN) 2026",
        "provider": "Jabatan Perkhidmatan Awam (JPA)",
        "official_portal_url": "https://esilav2.jpa.gov.my",
        "deadline": datetime(2026, 7, 15, 23, 59, 59, tzinfo=UTC),
        "status": "open",
        "freshness": "fresh",
        "last_verified_at": datetime.now(UTC),
    },
    {
        "id": "sch-petronas-pesp-2026",
        "source_id": "src-yayasan-petronas",
        "title": "Petronas Education Sponsorship Programme (PESP) 2026",
        "provider": "Yayasan PETRONAS",
        "official_portal_url": "https://educationsponsorship.petronas.com.my",
        "deadline": datetime(2026, 5, 31, 23, 59, 59, tzinfo=UTC),
        "status": "open",
        "freshness": "fresh",
        "last_verified_at": datetime.now(UTC),
    },
]

SAMPLE_VERSIONS = [
    {
        "id": "ver-khazanah-global-2026-v1",
        "scholarship_id": "sch-khazanah-global-2026",
        "application_cycle": "2026",
        "version_number": 1,
        "title": "Yayasan Khazanah Global Scholarship Programme 2026",
        "description": "Full scholarship for premier undergraduate degrees abroad.",
        "coverage_details": {"tuition": "Full", "living_allowance": True, "airfare": True},
        "deadline": datetime(2026, 6, 30, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-001",
        "approved_at": datetime.now(UTC),
    },
    {
        "id": "ver-jpa-ppn-2026-v1",
        "scholarship_id": "sch-jpa-ppn-2026",
        "application_cycle": "2026",
        "version_number": 1,
        "title": "JPA Program Penajaan Nasional (PPN) 2026",
        "description": "Federal civil service sponsorship for top SPM scorers.",
        "coverage_details": {"tuition": "Full", "stipend": "Monthly", "book_allowance": True},
        "deadline": datetime(2026, 7, 15, 23, 59, 59, tzinfo=UTC),
        "status": VersionStatus.APPROVED.value,
        "approved_by": "admin-demo-001",
        "approved_at": datetime.now(UTC),
    },
]

SAMPLE_REQUIREMENTS = [
    {
        "id": "req-khazanah-cgpa",
        "scholarship_version_id": "ver-khazanah-global-2026-v1",
        "type": "academic_cgpa",
        "operator": "gte",
        "value": 3.75,
        "is_mandatory": True,
        "source_excerpt": "Obtained a minimum CGPA of 3.75 or equivalent.",
        "is_subjective": False,
    },
    {
        "id": "req-khazanah-citizenship",
        "scholarship_version_id": "ver-khazanah-global-2026-v1",
        "type": "nationality",
        "operator": "eq",
        "value": "Malaysian",
        "is_mandatory": True,
        "source_excerpt": "Must be a Malaysian citizen.",
        "is_subjective": False,
    },
    {
        "id": "req-jpa-cgpa",
        "scholarship_version_id": "ver-jpa-ppn-2026-v1",
        "type": "academic_cgpa",
        "operator": "gte",
        "value": 3.80,
        "is_mandatory": True,
        "source_excerpt": "Memperoleh sekurang-kurangnya PNGK 3.80.",
        "is_subjective": False,
    },
    {
        "id": "req-jpa-citizenship",
        "scholarship_version_id": "ver-jpa-ppn-2026-v1",
        "type": "nationality",
        "operator": "eq",
        "value": "Malaysian",
        "is_mandatory": True,
        "source_excerpt": "Warganegara Malaysia.",
        "is_subjective": False,
    },
]

SAMPLE_DOCUMENTS = [
    {
        "id": "doc-khazanah-spm",
        "scholarship_version_id": "ver-khazanah-global-2026-v1",
        "name": "Certified SPM Result Slip",
        "description": "Original or certified copy of SPM examination results.",
        "is_mandatory": True,
        "format_instructions": "PDF under 5MB",
    },
    {
        "id": "doc-khazanah-ic",
        "scholarship_version_id": "ver-khazanah-global-2026-v1",
        "name": "Identity Card (MyKad) Copy",
        "description": "Front and back copy of MyKad.",
        "is_mandatory": True,
        "format_instructions": "PDF under 2MB",
    },
]

SAMPLE_RULES = [
    # Khazanah rules (legacy)
    {
        "id": "rule-khazanah-min-cgpa",
        "scholarship_id": "sch-khazanah-global-2026",
        "criterion_code": "min_cgpa",
        "rule_type": "numeric_threshold_min",
        "rule_parameters": {"field": "cgpa", "threshold": 3.75},
        "is_mandatory": True,
    },
    {
        "id": "rule-khazanah-citizenship",
        "scholarship_id": "sch-khazanah-global-2026",
        "criterion_code": "citizenship",
        "rule_type": "exact_match",
        "rule_parameters": {"field": "citizenship", "expected": "Malaysian"},
        "is_mandatory": True,
    },
    # JPA rules (legacy)
    {
        "id": "rule-jpa-min-cgpa",
        "scholarship_id": "sch-jpa-ppn-2026",
        "criterion_code": "min_cgpa",
        "rule_type": "numeric_threshold_min",
        "rule_parameters": {"field": "cgpa", "threshold": 3.80},
        "is_mandatory": True,
    },
    {
        "id": "rule-jpa-citizenship",
        "scholarship_id": "sch-jpa-ppn-2026",
        "criterion_code": "citizenship",
        "rule_type": "exact_match",
        "rule_parameters": {"field": "citizenship", "expected": "Malaysian"},
        "is_mandatory": True,
    },
    # Petronas rules (legacy)
    {
        "id": "rule-petronas-min-cgpa",
        "scholarship_id": "sch-petronas-pesp-2026",
        "criterion_code": "min_cgpa",
        "rule_type": "numeric_threshold_min",
        "rule_parameters": {"field": "cgpa", "threshold": 3.50},
        "is_mandatory": True,
    },
    {
        "id": "rule-petronas-income",
        "scholarship_id": "sch-petronas-pesp-2026",
        "criterion_code": "max_household_income",
        "rule_type": "numeric_threshold_max",
        "rule_parameters": {"field": "household_income", "threshold": 12000.0},
        "is_mandatory": False,
    },
]

DEMO_STUDENT_PROFILE = {
    "id": "profile-student-demo",
    "user_id": "student-demo-123",
    "study_level": "Undergraduate",
    "education_level": "Undergraduate",
    "nationality": "Malaysian",
    "citizenship": "Malaysian",
    "state_of_origin": "Penang",
    "field_of_study": "Software Engineering",
    "intended_field": "Computer Science",
    # Rule 5: Unknown values remain None, never 0
    "household_income": None,
    "cgpa": 3.82,
}

DEMO_APPLICATION = {
    "id": "app-student-demo-khazanah",
    "student_id": "student-demo-123",
    "scholarship_id": "sch-khazanah-global-2026",
    "stage": ApplicationStage.PREPARING.value,
    "notes": "Targeting Oxford or Cambridge Computer Science admissions.",
}

DEMO_TASKS = [
    {
        "id": "task-demo-transcript",
        "application_id": "app-student-demo-khazanah",
        "title": "Upload Academic Transcripts",
        "description": "Obtain certified true copy from university examination department.",
        "task_key": "task_upload_transcript",
        "is_completed": False,
        "due_date": datetime(2026, 5, 1, 23, 59, 59, tzinfo=UTC),
    },
    {
        "id": "task-demo-essay",
        "application_id": "app-student-demo-khazanah",
        "title": "Draft Leadership Essay",
        "description": "Draft personal statement highlighting Malaysian nation-building.",
        "task_key": "task_draft_leadership_essay",
        "is_completed": True,
        "completed_at": datetime.now(UTC),
    },
]

DEMO_COMPARISON_SET = {
    "id": "cmp-student-demo-1",
    "student_id": "student-demo-123",
    "name": "My Top Malaysian Engineering Sponsorships",
    "scholarship_ids": [
        "sch-khazanah-global-2026",
        "sch-jpa-ppn-2026",
        "sch-petronas-pesp-2026",
    ],
}

DEMO_NOTIFICATION = {
    "id": "notif-student-demo-1",
    "user_id": "student-demo-123",
    "title": "Yayasan Khazanah 2026 Application Cycle Announcement",
    "content": "Review the Yayasan Khazanah Global Scholarship 2026 requirements and key dates.",
    "notification_type": "deadline_warning",
    "is_read": False,
}


async def seed_data(session: AsyncSession | None = None) -> None:
    """Inserts baseline seed data and test fixtures into existing tables."""
    if session is not None:
        await _seed_with_async_session(session)
    else:
        logger.info("Initializing database session for seed data...")
        async with AsyncSessionLocal() as db_session:
            await _seed_with_async_session(db_session)


async def _seed_with_async_session(session: AsyncSession) -> None:
    """Internal helper to execute seed insertion in an async session."""
    # 1. Seed Users: Admins, baseline students, and boundary personas
    all_users = SAMPLE_USERS + FIXTURE_ADMINISTRATORS + FIXTURE_STUDENT_USERS
    for user_data in all_users:
        existing = await session.execute(select(User).where(User.id == user_data["id"]))
        if not existing.scalars().first():
            session.add(User(**user_data))
            logger.info(f"Seeded user: {user_data['full_name']} ({user_data['role']})")
    await session.flush()

    # 2. Seed Sources: 5 Monitored Malaysian Scholarship Sources
    all_sources = list(SAMPLE_SOURCES)
    for src in FIXTURE_SOURCES:
        if not any(s["id"] == src["id"] for s in all_sources):
            all_sources.append(src)
    for src_data in all_sources:
        existing = await session.execute(select(Source).where(Source.id == src_data["id"]))
        if not existing.scalars().first():
            session.add(Source(**src_data))
            logger.info(f"Seeded source: {src_data['name']}")
    await session.flush()

    # 3. Seed Scholarships: Baseline + 15 Fictional Demo Scholarships
    all_scholarships = SAMPLE_SCHOLARSHIPS + FIXTURE_SCHOLARSHIPS
    for item in all_scholarships:
        existing = await session.execute(
            select(Scholarship).where(Scholarship.id == item["id"])
        )
        if not existing.scalars().first():
            session.add(Scholarship(**item))
            logger.info(f"Seeded scholarship: {item['title']} (status: {item.get('status')})")
    await session.flush()

    # 4. Seed Scholarship Versions
    all_versions = SAMPLE_VERSIONS + FIXTURE_SCHOLARSHIP_VERSIONS
    for ver_data in all_versions:
        existing = await session.execute(
            select(ScholarshipVersion).where(ScholarshipVersion.id == ver_data["id"])
        )
        if not existing.scalars().first():
            session.add(ScholarshipVersion(**ver_data))
            logger.info(f"Seeded version: {ver_data['id']}")
    await session.flush()

    # 5. Seed Version Requirements
    all_requirements = SAMPLE_REQUIREMENTS + FIXTURE_REQUIREMENTS
    for req_data in all_requirements:
        existing = await session.execute(
            select(Requirement).where(Requirement.id == req_data["id"])
        )
        if not existing.scalars().first():
            session.add(Requirement(**req_data))
            logger.info(f"Seeded requirement: {req_data['id']} (type: {req_data.get('type')})")

    # 6. Seed Required Documents
    all_documents = SAMPLE_DOCUMENTS + FIXTURE_DOCUMENTS
    for doc_data in all_documents:
        existing = await session.execute(
            select(RequiredDocument).where(RequiredDocument.id == doc_data["id"])
        )
        if not existing.scalars().first():
            session.add(RequiredDocument(**doc_data))
            logger.info(f"Seeded required document: {doc_data['name']}")

    # 7. Seed Predefined Deterministic Eligibility Rules (Legacy compatibility)
    for rule_data in SAMPLE_RULES:
        existing = await session.execute(
            select(EligibilityRule).where(EligibilityRule.id == rule_data["id"])
        )
        if not existing.scalars().first():
            session.add(EligibilityRule(**rule_data))
            logger.info(f"Seeded legacy rule: {rule_data['id']}")
    await session.flush()

    # 8. Seed Student Profiles: Baseline + 5 Boundary Cases
    all_profiles = [DEMO_STUDENT_PROFILE] + FIXTURE_STUDENT_PROFILES
    for prof_data in all_profiles:
        existing_profile = await session.execute(
            select(StudentProfile).where(StudentProfile.user_id == prof_data["user_id"])
        )
        if not existing_profile.scalars().first():
            session.add(StudentProfile(**prof_data))
            income_label = (
                f"RM {prof_data['household_income']:,.2f}"
                if prof_data.get("household_income") is not None
                else "None (Rule 5 Null)"
            )
            logger.info(
                f"Seeded student profile for user: {prof_data['user_id']} (income: {income_label})"
            )
    await session.flush()

    # 9. Seed Demo Application
    existing_app_res = await session.execute(
        select(Application).where(
            Application.student_id == DEMO_APPLICATION["student_id"],
            Application.scholarship_id == DEMO_APPLICATION["scholarship_id"],
        )
    )
    app_row = existing_app_res.scalars().first()
    if not app_row:
        app_row = Application(**DEMO_APPLICATION)
        session.add(app_row)
        await session.flush()
        logger.info("Seeded demo application in Preparing stage")
    else:
        logger.info(f"Reusing existing demo application: {app_row.id}")

    # 10. Seed Application Tasks using the resolved app_row.id
    for task_data in DEMO_TASKS:
        task_payload = dict(task_data)
        task_payload["application_id"] = app_row.id
        existing = await session.execute(
            select(ApplicationTask).where(
                ApplicationTask.application_id == app_row.id,
                ApplicationTask.task_key == task_payload["task_key"],
            )
        )
        if not existing.scalars().first():
            session.add(ApplicationTask(**task_payload))
            logger.info(f"Seeded application task: {task_payload['title']}")
    await session.flush()

    # 11. Seed Demo Comparison Set
    existing_cmp = await session.execute(
        select(ComparisonSet).where(ComparisonSet.id == DEMO_COMPARISON_SET["id"])
    )
    if not existing_cmp.scalars().first():
        session.add(ComparisonSet(**DEMO_COMPARISON_SET))
        logger.info("Seeded demo student comparison set")

    # 12. Seed Demo Notification
    existing_notif = await session.execute(
        select(Notification).where(Notification.id == DEMO_NOTIFICATION["id"])
    )
    if not existing_notif.scalars().first():
        session.add(Notification(**DEMO_NOTIFICATION))
        logger.info("Seeded demo student notification")

    await session.commit()
    logger.info("Seed data processing completed successfully.")


def seed_data_sync(session: Session) -> None:
    """
    Synchronous seed insertion helper for synchronous SQLite testing and verification.
    Seeds users, sources, 15 fictional scholarships, 5 boundary student profiles, and administrators.
    """
    # 1. Users
    all_users = SAMPLE_USERS + FIXTURE_ADMINISTRATORS + FIXTURE_STUDENT_USERS
    for user_data in all_users:
        if not session.execute(select(User).where(User.id == user_data["id"])).scalars().first():
            session.add(User(**user_data))
    session.flush()

    # 2. Sources
    all_sources = list(SAMPLE_SOURCES)
    for src in FIXTURE_SOURCES:
        if not any(s["id"] == src["id"] for s in all_sources):
            all_sources.append(src)
    for src_data in all_sources:
        if not session.execute(select(Source).where(Source.id == src_data["id"])).scalars().first():
            session.add(Source(**src_data))
    session.flush()

    # 3. Scholarships
    all_scholarships = SAMPLE_SCHOLARSHIPS + FIXTURE_SCHOLARSHIPS
    for item in all_scholarships:
        if not session.execute(select(Scholarship).where(Scholarship.id == item["id"])).scalars().first():
            session.add(Scholarship(**item))
    session.flush()

    # 4. Scholarship Versions
    all_versions = SAMPLE_VERSIONS + FIXTURE_SCHOLARSHIP_VERSIONS
    for ver_data in all_versions:
        if not session.execute(select(ScholarshipVersion).where(ScholarshipVersion.id == ver_data["id"])).scalars().first():
            session.add(ScholarshipVersion(**ver_data))
    session.flush()

    # 5. Requirements
    all_requirements = SAMPLE_REQUIREMENTS + FIXTURE_REQUIREMENTS
    for req_data in all_requirements:
        if not session.execute(select(Requirement).where(Requirement.id == req_data["id"])).scalars().first():
            session.add(Requirement(**req_data))

    # 6. Documents
    all_documents = SAMPLE_DOCUMENTS + FIXTURE_DOCUMENTS
    for doc_data in all_documents:
        if not session.execute(select(RequiredDocument).where(RequiredDocument.id == doc_data["id"])).scalars().first():
            session.add(RequiredDocument(**doc_data))

    # 7. Rules
    for rule_data in SAMPLE_RULES:
        if not session.execute(select(EligibilityRule).where(EligibilityRule.id == rule_data["id"])).scalars().first():
            session.add(EligibilityRule(**rule_data))
    session.flush()

    # 8. Profiles
    all_profiles = [DEMO_STUDENT_PROFILE] + FIXTURE_STUDENT_PROFILES
    for prof_data in all_profiles:
        if not session.execute(select(StudentProfile).where(StudentProfile.user_id == prof_data["user_id"])).scalars().first():
            session.add(StudentProfile(**prof_data))
    session.flush()

    # 9. Applications
    existing_app = session.execute(
        select(Application).where(
            Application.student_id == DEMO_APPLICATION["student_id"],
            Application.scholarship_id == DEMO_APPLICATION["scholarship_id"],
        )
    ).scalars().first()
    if not existing_app:
        app_row = Application(**DEMO_APPLICATION)
        session.add(app_row)
        session.flush()
    else:
        app_row = existing_app

    # 10. Tasks
    for task_data in DEMO_TASKS:
        task_payload = dict(task_data)
        task_payload["application_id"] = app_row.id
        if not session.execute(
            select(ApplicationTask).where(
                ApplicationTask.application_id == app_row.id,
                ApplicationTask.task_key == task_payload["task_key"],
            )
        ).scalars().first():
            session.add(ApplicationTask(**task_payload))
    session.flush()

    # 11. Comparison Set
    if not session.execute(select(ComparisonSet).where(ComparisonSet.id == DEMO_COMPARISON_SET["id"])).scalars().first():
        session.add(ComparisonSet(**DEMO_COMPARISON_SET))

    # 12. Notification
    if not session.execute(select(Notification).where(Notification.id == DEMO_NOTIFICATION["id"])).scalars().first():
        session.add(Notification(**DEMO_NOTIFICATION))

    session.commit()
    logger.info("Synchronous seed data processing completed successfully.")


def main() -> None:
    """CLI entrypoint for database seeding."""
    parser = argparse.ArgumentParser(
        description="ScholarPal database seed command. Populates sources, fictional scholarships, administrators, and boundary student profiles."
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print summary count of seeded fixtures.",
    )
    args = parser.parse_args()

    if args.summary:
        print("ScholarPal Fixture Data Summary:")
        print(f"- Monitored Sources: {len(FIXTURE_SOURCES)}")
        print(f"- Administrators: {len(FIXTURE_ADMINISTRATORS)}")
        print(f"- Boundary Student Profiles: {len(FIXTURE_STUDENT_PROFILES)}")
        print(f"- Fictional Scholarships (Demo Flagged): {len(FIXTURE_SCHOLARSHIPS)}")
        print(f"- Scholarship Versions: {len(FIXTURE_SCHOLARSHIP_VERSIONS)}")
        print(f"- Deterministic Requirements: {len(FIXTURE_REQUIREMENTS)}")
        print(f"- Required Documents: {len(FIXTURE_DOCUMENTS)}")
        return

    asyncio.run(seed_data())


if __name__ == "__main__":
    main()

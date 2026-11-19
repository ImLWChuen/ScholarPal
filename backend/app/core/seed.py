"""
Seed data entry point for ScholarPal PostgreSQL database.
Populates baseline users, sources, scholarships, versions, requirements, and applications.

Adheres strictly to ScholarPal Non-Negotiable Rules:
- Rule 1 & 2: Predefined rules with 3-state evaluation (satisfied, unmet, unresolved).
- Rule 4: Preserves records with 'fresh' freshness.
- Rule 5: Unknown values remain None, never zero.
- Rule 7: External provider submission portal URLs.
- Rule 8: Student ownership on student records.
"""

import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
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
        "source_id": "src-yayasan-khazanah",
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
    "title": "Application Cycle 2026 Open",
    "content": "Yayasan Khazanah Global Scholarship 2026 is now open for submissions.",
    "notification_type": "deadline_warning",
    "is_read": False,
}


async def seed_data() -> None:
    """Inserts baseline seed data into existing tables."""
    logger.info("Initializing database session for seed data...")
    async with AsyncSessionLocal() as session:
        # 1. Seed Users
        for user_data in SAMPLE_USERS:
            existing = await session.execute(select(User).where(User.id == user_data["id"]))
            if not existing.scalars().first():
                session.add(User(**user_data))
                logger.info(f"Seeded user: {user_data['full_name']}")

        # 2. Seed Sources
        for src_data in SAMPLE_SOURCES:
            existing = await session.execute(select(Source).where(Source.id == src_data["id"]))
            if not existing.scalars().first():
                session.add(Source(**src_data))
                logger.info(f"Seeded source: {src_data['name']}")

        # 3. Seed Scholarships
        for item in SAMPLE_SCHOLARSHIPS:
            existing = await session.execute(
                select(Scholarship).where(Scholarship.id == item["id"])
            )
            if not existing.scalars().first():
                session.add(Scholarship(**item))
                logger.info(f"Seeded scholarship: {item['title']}")

        # 4. Seed Scholarship Versions
        for ver_data in SAMPLE_VERSIONS:
            existing = await session.execute(
                select(ScholarshipVersion).where(ScholarshipVersion.id == ver_data["id"])
            )
            if not existing.scalars().first():
                session.add(ScholarshipVersion(**ver_data))
                logger.info(f"Seeded version: {ver_data['id']}")

        # 5. Seed Version Requirements
        for req_data in SAMPLE_REQUIREMENTS:
            existing = await session.execute(
                select(Requirement).where(Requirement.id == req_data["id"])
            )
            if not existing.scalars().first():
                session.add(Requirement(**req_data))
                logger.info(f"Seeded requirement: {req_data['id']}")

        # 6. Seed Required Documents
        for doc_data in SAMPLE_DOCUMENTS:
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

        # 8. Seed Demo Student Profile
        existing_profile = await session.execute(
            select(StudentProfile).where(StudentProfile.user_id == DEMO_STUDENT_PROFILE["user_id"])
        )
        if not existing_profile.scalars().first():
            session.add(StudentProfile(**DEMO_STUDENT_PROFILE))
            logger.info("Seeded demo student profile (household_income stays None as per Rule 5)")

        # 9. Seed Demo Application
        existing_app = await session.execute(
            select(Application).where(Application.id == DEMO_APPLICATION["id"])
        )
        if not existing_app.scalars().first():
            session.add(Application(**DEMO_APPLICATION))
            logger.info("Seeded demo application in Preparing stage")

        # 10. Seed Application Tasks
        for task_data in DEMO_TASKS:
            existing = await session.execute(
                select(ApplicationTask).where(ApplicationTask.id == task_data["id"])
            )
            if not existing.scalars().first():
                session.add(ApplicationTask(**task_data))
                logger.info(f"Seeded application task: {task_data['title']}")

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


if __name__ == "__main__":
    asyncio.run(seed_data())

"""
Seed data entry point for ScholarPal PostgreSQL database.
Populates baseline scholarship records, deterministic eligibility rules, and demo records.

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

from app.core.db import AsyncSessionLocal, Base, engine
from app.domain.comparison.models import ComparisonSet
from app.domain.eligibility_impact.models import EligibilityRule
from app.domain.profile_preparation.models import StudentProfile
from app.domain.scholarship_discovery.models import Scholarship

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

SAMPLE_SCHOLARSHIPS = [
    {
        "id": "sch-khazanah-global-2026",
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
        "title": "Petronas Education Sponsorship Programme (PESP) 2026",
        "provider": "Yayasan PETRONAS",
        "official_portal_url": "https://educationsponsorship.petronas.com.my",
        "deadline": datetime(2026, 5, 31, 23, 59, 59, tzinfo=UTC),
        "status": "open",
        "freshness": "fresh",
        "last_verified_at": datetime.now(UTC),
    },
]

SAMPLE_RULES = [
    # Khazanah rules
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
    # JPA rules
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
    # Petronas rules
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
    "education_level": "Undergraduate",
    "citizenship": "Malaysian",
    "state_of_origin": "Penang",
    # Rule 5: Unknown values remain None, never 0
    "household_income": None,
    "cgpa": 3.82,
}

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


async def seed_data() -> None:
    """Creates tables if missing and inserts baseline seed data."""
    logger.info("Initializing database connection...")
    async with engine.begin() as conn:
        # Ensure schema tables exist
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Seed Scholarships
        for item in SAMPLE_SCHOLARSHIPS:
            existing = await session.execute(
                select(Scholarship).where(Scholarship.id == item["id"])
            )
            if not existing.scalars().first():
                session.add(Scholarship(**item))
                logger.info(f"Seeded scholarship: {item['title']}")

        # 2. Seed Predefined Deterministic Eligibility Rules
        for rule_data in SAMPLE_RULES:
            existing = await session.execute(
                select(EligibilityRule).where(EligibilityRule.id == rule_data["id"])
            )
            if not existing.scalars().first():
                session.add(EligibilityRule(**rule_data))
                logger.info(f"Seeded rule: {rule_data['id']}")

        # 3. Seed Demo Student Profile
        existing_profile = await session.execute(
            select(StudentProfile).where(StudentProfile.user_id == DEMO_STUDENT_PROFILE["user_id"])
        )
        if not existing_profile.scalars().first():
            session.add(StudentProfile(**DEMO_STUDENT_PROFILE))
            logger.info("Seeded demo student profile (household_income stays None as per Rule 5)")

        # 4. Seed Demo Comparison Set
        existing_cmp = await session.execute(
            select(ComparisonSet).where(ComparisonSet.id == DEMO_COMPARISON_SET["id"])
        )
        if not existing_cmp.scalars().first():
            session.add(ComparisonSet(**DEMO_COMPARISON_SET))
            logger.info("Seeded demo student comparison set")

        await session.commit()
        logger.info("Seed data processing completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_data())

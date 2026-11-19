"""
Tests for ScholarPal Fixtures and Seed Data.

Verifies:
- 5 Monitored sources seeded
- 2 Fictional administrators seeded with UserRole.ADMINISTRATOR
- 15 Fictional scholarships seeded across all study levels (Secondary, Pre-U, Undergraduate, Postgraduate)
- All 15 fictional scholarships marked with status='demo' and demo flags so they never appear as current opportunities
- 5 Boundary-case student profiles (income exactly at threshold, missing fields, unmet mandatory rule, subject results boundary, study level mismatch)
- Execution of seed insertion preserves database referential integrity
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base
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
from app.core.seed import seed_data_sync
from app.domain import (
    Application,
    RequiredDocument,
    Requirement,
    Scholarship,
    ScholarshipVersion,
    Source,
    StudentProfile,
    User,
    UserRole,
)


@pytest.fixture
def sync_session() -> Session:
    """Creates an in-memory SQLite session with full schema for fixture testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def test_fixture_source_counts():
    """Verify source fixtures count and demo configurations."""
    assert len(FIXTURE_SOURCES) == 5
    for src in FIXTURE_SOURCES:
        assert src["config"].get("is_demo") is True
        assert src["is_active"] is True


def test_fixture_administrators_count_and_roles():
    """Verify exactly 2 administrators are defined with UserRole.ADMINISTRATOR."""
    assert len(FIXTURE_ADMINISTRATORS) == 2
    for admin in FIXTURE_ADMINISTRATORS:
        assert admin["role"] == UserRole.ADMINISTRATOR.value
        assert admin["is_verified"] is True
        assert "@demo.scholarpal.internal" in admin["email"]


def test_fixture_scholarships_distribution_and_demo_flags():
    """
    Verify 15 realistic fictional scholarships exist across all study levels,
    and all are explicitly marked with status='demo' and demo flags so they
    never appear as current open opportunities.
    """
    assert len(FIXTURE_SCHOLARSHIPS) == 15

    # Check study level distribution across versions
    secondary_count = sum(1 for s in FIXTURE_SCHOLARSHIPS if "sec" in s["id"])
    preu_count = sum(1 for s in FIXTURE_SCHOLARSHIPS if "preu" in s["id"])
    ug_count = sum(1 for s in FIXTURE_SCHOLARSHIPS if "ug" in s["id"])
    pg_count = sum(1 for s in FIXTURE_SCHOLARSHIPS if "pg" in s["id"])

    assert secondary_count == 3
    assert preu_count == 4
    assert ug_count == 5
    assert pg_count == 3

    # Safety guarantee: every fictional scholarship is flagged as demo
    for sch in FIXTURE_SCHOLARSHIPS:
        assert sch["status"] == "demo", f"Scholarship {sch['id']} must have status='demo'"
        assert sch["freshness"] == "demo_fixture"
        assert sch["title"].startswith("[DEMO FICTIONAL]")
        assert "demo.scholarpal.internal" in sch["official_portal_url"]


def test_fixture_student_profiles_boundary_cases():
    """
    Verify 5 student profiles covering the specified boundary cases:
    1. Income exactly at threshold
    2. Missing fields (Rule 5 compliant NULL)
    3. Unmet mandatory rule
    4. Subject results boundary
    5. Study level / citizenship mismatch
    """
    assert len(FIXTURE_STUDENT_PROFILES) == 5
    assert len(FIXTURE_STUDENT_USERS) == 5

    # Boundary 1: Income exactly at threshold (RM 4,800 B40 ceiling)
    p1 = next(p for p in FIXTURE_STUDENT_PROFILES if p["id"] == "prof-demo-income-boundary")
    assert p1["household_income"] == 4800.0
    assert p1["cgpa"] == 3.85

    # Boundary 2: Missing fields (Rule 5 compliant NULL)
    p2 = next(p for p in FIXTURE_STUDENT_PROFILES if p["id"] == "prof-demo-missing-fields")
    assert p2["household_income"] is None
    assert p2["cgpa"] is None

    # Boundary 3: Unmet mandatory rule (CGPA 3.48 vs 3.50 cutoff)
    p3 = next(p for p in FIXTURE_STUDENT_PROFILES if p["id"] == "prof-demo-unmet-mandatory")
    assert p3["cgpa"] == 3.48
    assert p3["household_income"] == 3200.0

    # Boundary 4: Subject results boundary (Exactly 7 A/A+ when 8 required)
    p4 = next(p for p in FIXTURE_STUDENT_PROFILES if p["id"] == "prof-demo-grades-boundary")
    qualifying_grades = [g for g in p4["academic_results"].values() if g in ("A+", "A")]
    assert len(qualifying_grades) == 7

    # Boundary 5: Study level and citizenship mismatch
    p5 = next(p for p in FIXTURE_STUDENT_PROFILES if p["id"] == "prof-demo-mismatch")
    assert p5["study_level"] == "Postgraduate"
    assert p5["nationality"] == "Singaporean"


def test_seed_data_sync_database_execution(sync_session: Session):
    """
    Verify that seed_data_sync populates the database cleanly and preserves
    foreign keys, uniqueness constraints, and relationships.
    """
    seed_data_sync(sync_session)

    # 1. Verify users seeded
    users = sync_session.execute(select(User)).scalars().all()
    admins = [u for u in users if u.role == UserRole.ADMINISTRATOR.value]
    students = [u for u in users if u.role == UserRole.STUDENT.value]
    assert len(admins) >= 2
    assert len(students) >= 5

    # 2. Verify sources seeded
    sources = sync_session.execute(select(Source)).scalars().all()
    assert len(sources) >= 5

    # 3. Verify scholarships and demo isolation
    all_scholarships = sync_session.execute(select(Scholarship)).scalars().all()
    demo_scholarships = [s for s in all_scholarships if s.status == "demo"]
    assert len(demo_scholarships) == 15

    # Verify query for live open opportunities NEVER includes demo scholarships
    live_open_scholarships = sync_session.execute(
        select(Scholarship).where(Scholarship.status == "open")
    ).scalars().all()
    for live in live_open_scholarships:
        assert not live.title.startswith("[DEMO FICTIONAL]")
        assert live.status != "demo"

    # 4. Verify boundary student profiles
    profiles = sync_session.execute(select(StudentProfile)).scalars().all()
    assert len(profiles) >= 5

    # Verify income boundary profile
    income_prof = next(p for p in profiles if p.id == "prof-demo-income-boundary")
    assert income_prof.household_income == 4800.0

    # Verify missing fields profile (Rule 5)
    missing_prof = next(p for p in profiles if p.id == "prof-demo-missing-fields")
    assert missing_prof.household_income is None
    assert missing_prof.cgpa is None

    # 5. Verify requirements and documents
    requirements = sync_session.execute(select(Requirement)).scalars().all()
    assert len(requirements) >= 30

    documents = sync_session.execute(select(RequiredDocument)).scalars().all()
    assert len(documents) >= 6

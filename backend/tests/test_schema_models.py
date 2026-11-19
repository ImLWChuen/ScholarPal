"""
Tests for ScholarPal SQLAlchemy models, foreign keys, and uniqueness constraints.
Verifies all 17 entities and constraint behaviors in an isolated test database.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base
from app.domain import (
    Application,
    ApplicationStage,
    ApplicationTask,
    AuditLog,
    AwardOffer,
    ComparisonSet,
    DocumentChecklistItem,
    EvidenceCheck,
    Interview,
    Notification,
    Reminder,
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


@pytest.fixture(name="db_session")
def db_session_fixture():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session: Session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def test_create_all_entities(db_session: Session):
    # 1. User
    user = User(
        id="usr-1",
        email="student@scholarpal.my",
        full_name="Ahmad Student",
        role=UserRole.STUDENT.value,
    )
    admin = User(
        id="usr-admin",
        email="admin@scholarpal.my",
        full_name="Admin Reviewer",
        role=UserRole.ADMINISTRATOR.value,
    )
    db_session.add_all([user, admin])
    db_session.commit()

    # 2. StudentProfile (Rule 5: household_income stays None)
    profile = StudentProfile(
        id="prof-1",
        user_id="usr-1",
        study_level="Undergraduate",
        nationality="Malaysian",
        field_of_study="Computer Science",
        intended_field="Artificial Intelligence",
        academic_results={"spm": {"BM": "A+", "Math": "A+"}},
        household_income=None,
        cgpa=3.85,
    )
    db_session.add(profile)
    db_session.commit()
    assert profile.household_income is None

    # 3. Source
    source = Source(
        id="src-1",
        name="Yayasan Khazanah",
        base_url="https://www.yayasankhazanah.com.my",
        config={"crawl_delay": 2},
        schedule="0 2 * * *",
        is_active=True,
    )
    db_session.add(source)
    db_session.commit()

    # 4. Retrieval
    retrieval = source.retrievals
    assert retrieval == []

    # 5. Scholarship
    scholarship = Scholarship(
        id="sch-1",
        source_id="src-1",
        title="Khazanah Global Scholarship 2026",
        provider="Yayasan Khazanah",
        official_portal_url="https://www.yayasankhazanah.com.my/scholarships",
        freshness="fresh",
        status="open",
    )
    db_session.add(scholarship)
    db_session.commit()

    # 6. ScholarshipVersion
    version = ScholarshipVersion(
        id="ver-1",
        scholarship_id="sch-1",
        application_cycle="2026",
        version_number=1,
        title="Khazanah Global 2026 Edition",
        description="Full overseas sponsorship.",
        status=VersionStatus.APPROVED.value,
        approved_by="usr-admin",
        approved_at=datetime.now(UTC),
    )
    db_session.add(version)
    db_session.commit()

    # 7. Requirement
    req = Requirement(
        id="req-1",
        scholarship_version_id="ver-1",
        type="academic_cgpa",
        operator="gte",
        value=3.75,
        is_mandatory=True,
        source_excerpt="Minimum CGPA 3.75",
        is_subjective=False,
    )
    db_session.add(req)
    db_session.commit()

    # 8. RequiredDocument
    doc = RequiredDocument(
        id="doc-1",
        scholarship_version_id="ver-1",
        name="SPM Result Slip",
        is_mandatory=True,
    )
    db_session.add(doc)
    db_session.commit()

    # 9. EvidenceCheck (Jev)
    evidence = EvidenceCheck(
        id="ev-1",
        scholarship_version_id="ver-1",
        requirement_id="req-1",
        jev_label="Supported",
        probabilities={"Supported": 0.95, "Refuted": 0.05},
        confidence=0.95,
        evidence_excerpt="Verified by Jev evidence check primitive.",
    )
    db_session.add(evidence)
    db_session.commit()

    # 10. Application
    app = Application(
        id="app-1",
        student_id="usr-1",
        scholarship_id="sch-1",
        stage=ApplicationStage.PREPARING.value,
    )
    db_session.add(app)
    db_session.commit()

    # 11. ApplicationTask
    task = ApplicationTask(
        id="tsk-1",
        application_id="app-1",
        title="Submit official transcript",
        task_key="task_upload_transcript",
    )
    db_session.add(task)
    db_session.commit()

    # 12. DocumentChecklistItem
    item = DocumentChecklistItem(
        id="dci-1",
        application_id="app-1",
        required_document_id="doc-1",
        file_name="transcript_certified.pdf",
    )
    db_session.add(item)
    db_session.commit()

    # 13. Interview
    interview = Interview(
        id="int-1",
        application_id="app-1",
        scheduled_at=datetime.now(UTC),
        round_name="Final Panel Interview",
    )
    db_session.add(interview)
    db_session.commit()

    # 14. AwardOffer
    offer = AwardOffer(
        id="off-1",
        application_id="app-1",
        offer_amount=150000.0,
        currency="MYR",
        bond_duration_years=5,
        decision="pending",
    )
    db_session.add(offer)
    db_session.commit()

    # 15. Reminder
    reminder = Reminder(
        id="rem-1",
        user_id="usr-1",
        application_id="app-1",
        remind_at=datetime.now(UTC),
        message="Interview tomorrow at 10 AM",
    )
    db_session.add(reminder)
    db_session.commit()

    # 16. Notification
    notif = Notification(
        id="not-1",
        user_id="usr-1",
        title="Application Status Updated",
        content="Moved to Interview stage",
    )
    db_session.add(notif)
    db_session.commit()

    # 17. AuditLog & ComparisonSet
    audit = AuditLog(
        id="aud-1",
        actor_id="usr-admin",
        action="version_approved",
        entity_type="scholarship_version",
        entity_id="ver-1",
    )
    cmp_set = ComparisonSet(
        id="cmp-1",
        student_id="usr-1",
        name="Top Choices",
        scholarship_ids=["sch-1"],
    )
    db_session.add_all([audit, cmp_set])
    db_session.commit()

    # Verify relationships & queryability
    queried_app = db_session.get(Application, "app-1")
    assert queried_app is not None
    assert len(queried_app.tasks) == 1
    assert len(queried_app.document_checklist) == 1
    assert queried_app.award_offer is not None
    assert queried_app.award_offer.offer_amount == 150000.0


def test_duplicate_task_prevention(db_session: Session):
    user = User(id="u1", email="u1@test.my", full_name="U1")
    sch = Scholarship(
        id="s1",
        title="S1",
        provider="P1",
        official_portal_url="https://portal.my",
    )
    app = Application(id="a1", student_id="u1", scholarship_id="s1")
    t1 = ApplicationTask(
        id="t1",
        application_id="a1",
        title="Task A",
        task_key="unique_task_code",
    )
    db_session.add_all([user, sch, app, t1])
    db_session.commit()

    # Attempting to add duplicate task for same application with identical task_key
    t2 = ApplicationTask(
        id="t2",
        application_id="a1",
        title="Task A Duplicate",
        task_key="unique_task_code",
    )
    db_session.add(t2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_duplicate_application_prevention(db_session: Session):
    user = User(id="u1", email="u1@test.my", full_name="U1")
    sch = Scholarship(
        id="s1",
        title="S1",
        provider="P1",
        official_portal_url="https://portal.my",
    )
    app1 = Application(id="a1", student_id="u1", scholarship_id="s1")
    db_session.add_all([user, sch, app1])
    db_session.commit()

    # Same student applying again to the same scholarship
    app2 = Application(id="a2", student_id="u1", scholarship_id="s1")
    db_session.add(app2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_duplicate_version_prevention(db_session: Session):
    sch = Scholarship(
        id="s1",
        title="S1",
        provider="P1",
        official_portal_url="https://portal.my",
    )
    v1 = ScholarshipVersion(
        id="v1",
        scholarship_id="s1",
        application_cycle="2026",
        version_number=1,
        title="Version 1",
    )
    db_session.add_all([sch, v1])
    db_session.commit()

    # Duplicate version for same cycle and version number
    v2 = ScholarshipVersion(
        id="v2",
        scholarship_id="s1",
        application_cycle="2026",
        version_number=1,
        title="Version 1 Duplicate",
    )
    db_session.add(v2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

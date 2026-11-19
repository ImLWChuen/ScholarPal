"""
Tests for ScholarPal SQLAlchemy models, foreign keys, and uniqueness constraints.
Verifies all 17 entities and constraint behaviors in an isolated test database.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import Engine, create_engine, event, inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
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
    RetrievalProcessingClaim,
    Scholarship,
    ScholarshipVersion,
    Source,
    StudentProfile,
    User,
    UserRole,
    VersionStatus,
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraint enforcement in SQLite connections."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


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
        is_verified=True,
    )
    admin = User(
        id="usr-admin",
        email="admin@scholarpal.my",
        full_name="Admin Reviewer",
        role=UserRole.ADMINISTRATOR.value,
        is_verified=True,
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

    # 4. Retrieval & RetrievalProcessingClaim
    claim = RetrievalProcessingClaim(
        id="claim-1",
        source_id="src-1",
        url="https://www.yayasankhazanah.com.my/scholarships",
        content_hash="a" * 64,
    )
    db_session.add(claim)
    db_session.commit()

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
        portal_submission_reference="REF-KHZ-2026-001",
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
    assert queried_app.submission_reference == "REF-KHZ-2026-001"
    assert queried_app.portal_submission_reference == "REF-KHZ-2026-001"


def test_foreign_key_enforcement(db_session: Session):
    # StudentProfile with invalid user_id must fail FK constraint
    invalid_profile = StudentProfile(
        id="prof-invalid",
        user_id="non-existent-user",
        study_level="Undergraduate",
    )
    db_session.add(invalid_profile)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Application with invalid student_id must fail FK constraint
    sch = Scholarship(
        id="sch-fk-1",
        title="Sch FK",
        provider="Provider",
        official_portal_url="https://portal.my",
    )
    db_session.add(sch)
    db_session.commit()

    invalid_app = Application(
        id="app-invalid",
        student_id="non-existent-user",
        scholarship_id="sch-fk-1",
    )
    db_session.add(invalid_app)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_cascade_deletions(db_session: Session):
    user = User(id="u-del", email="u-del@test.my", full_name="User Delete")
    sch = Scholarship(
        id="sch-del",
        title="Sch Delete",
        provider="Provider",
        official_portal_url="https://portal.my",
    )
    db_session.add_all([user, sch])
    db_session.commit()

    profile = StudentProfile(id="prof-del", user_id="u-del")
    ver = ScholarshipVersion(
        id="ver-del",
        scholarship_id="sch-del",
        application_cycle="2026",
        version_number=1,
        title="Version to Delete",
    )
    app = Application(id="app-del", student_id="u-del", scholarship_id="sch-del")
    db_session.add_all([profile, ver, app])
    db_session.commit()

    # Deleting User must cascade-delete profile and application
    db_session.delete(user)
    db_session.commit()
    assert db_session.get(StudentProfile, "prof-del") is None
    assert db_session.get(Application, "app-del") is None

    # Deleting Scholarship must cascade-delete version
    db_session.delete(sch)
    db_session.commit()
    assert db_session.get(ScholarshipVersion, "ver-del") is None


def test_approved_version_immutability(db_session: Session):
    sch = Scholarship(
        id="sch-imm",
        title="Sch Immutability",
        provider="Provider",
        official_portal_url="https://portal.my",
    )
    ver = ScholarshipVersion(
        id="ver-imm",
        scholarship_id="sch-imm",
        application_cycle="2026",
        version_number=1,
        title="Original Title",
        status=VersionStatus.DRAFT.value,
    )
    db_session.add_all([sch, ver])
    db_session.commit()

    # Modifying draft version is permitted
    ver.title = "Updated Draft Title"
    db_session.commit()
    assert ver.title == "Updated Draft Title"

    # Status transitions (draft -> pending -> approved) are permitted
    ver.status = VersionStatus.PENDING.value
    db_session.commit()
    ver.status = VersionStatus.APPROVED.value
    db_session.commit()

    # Once approved, content mutation must be blocked by immutability listener
    ver.title = "Mutated After Approval"
    with pytest.raises(
        ValueError, match="is immutable. Content modifications must be published as a new version"
    ):
        db_session.commit()
    db_session.rollback()


def test_document_slot_integrity(db_session: Session):
    user = User(id="u-slot", email="u-slot@test.my", full_name="User Slot")
    sch1 = Scholarship(
        id="sch-slot-1",
        title="Sch 1",
        provider="P1",
        official_portal_url="https://p1.my",
    )
    sch2 = Scholarship(
        id="sch-slot-2",
        title="Sch 2",
        provider="P2",
        official_portal_url="https://p2.my",
    )
    ver1 = ScholarshipVersion(
        id="ver-slot-1",
        scholarship_id="sch-slot-1",
        application_cycle="2026",
        version_number=1,
        title="V1",
    )
    ver2 = ScholarshipVersion(
        id="ver-slot-2",
        scholarship_id="sch-slot-2",
        application_cycle="2026",
        version_number=1,
        title="V2",
    )
    doc1 = RequiredDocument(id="doc-slot-1", scholarship_version_id="ver-slot-1", name="Doc 1")
    doc2 = RequiredDocument(id="doc-slot-2", scholarship_version_id="ver-slot-2", name="Doc 2")
    app1 = Application(id="app-slot-1", student_id="u-slot", scholarship_id="sch-slot-1")

    db_session.add_all([user, sch1, sch2, ver1, ver2, doc1, doc2, app1])
    db_session.commit()

    # Valid slot: app1 (sch1) references doc1 (ver1 belonging to sch1)
    valid_item = DocumentChecklistItem(
        id="dci-slot-valid",
        application_id="app-slot-1",
        required_document_id="doc-slot-1",
    )
    db_session.add(valid_item)
    db_session.commit()

    # Invalid slot: app1 (sch1) references doc2 (ver2 belonging to sch2)
    invalid_item = DocumentChecklistItem(
        id="dci-slot-invalid",
        application_id="app-slot-1",
        required_document_id="doc-slot-2",
    )
    db_session.add(invalid_item)
    with pytest.raises(ValueError, match="Slot integrity violation"):
        db_session.commit()
    db_session.rollback()


def test_partial_unique_application(db_session: Session):
    user = User(id="u-part", email="u-part@test.my", full_name="User Part")
    sch = Scholarship(
        id="sch-part",
        title="Sch Part",
        provider="P",
        official_portal_url="https://p.my",
    )
    app1 = Application(
        id="app-part-1",
        student_id="u-part",
        scholarship_id="sch-part",
        stage=ApplicationStage.PREPARING.value,
    )
    db_session.add_all([user, sch, app1])
    db_session.commit()

    # Duplicate active application for same (student, scholarship) must be rejected
    app2 = Application(
        id="app-part-2",
        student_id="u-part",
        scholarship_id="sch-part",
        stage=ApplicationStage.SUBMITTED.value,
    )
    db_session.add(app2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # If previous application was Withdrawn, a new application is permitted
    app1.stage = ApplicationStage.WITHDRAWN.value
    db_session.commit()

    app3 = Application(
        id="app-part-3",
        student_id="u-part",
        scholarship_id="sch-part",
        stage=ApplicationStage.PREPARING.value,
    )
    db_session.add(app3)
    db_session.commit()
    assert db_session.get(Application, "app-part-3") is not None


def test_retrieval_processing_claim_uniqueness(db_session: Session):
    source = Source(
        id="src-claim",
        name="Source Claim",
        base_url="https://claim.my",
        config={},
    )
    db_session.add(source)
    db_session.commit()

    claim1 = RetrievalProcessingClaim(
        id="clm-1",
        source_id="src-claim",
        url="https://claim.my/sch-1",
        content_hash="hash12345",
    )
    db_session.add(claim1)
    db_session.commit()

    # Duplicate claim for same (source_id, url, content_hash) must be rejected
    claim2 = RetrievalProcessingClaim(
        id="clm-2",
        source_id="src-claim",
        url="https://claim.my/sch-1",
        content_hash="hash12345",
    )
    db_session.add(claim2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_evidence_check_composite_version_req_fk(db_session: Session):
    sch = Scholarship(
        id="sch-ev",
        title="Sch EV",
        provider="P",
        official_portal_url="https://p.my",
    )
    v1 = ScholarshipVersion(
        id="v-ev-1",
        scholarship_id="sch-ev",
        application_cycle="2026",
        version_number=1,
        title="V1",
    )
    v2 = ScholarshipVersion(
        id="v-ev-2",
        scholarship_id="sch-ev",
        application_cycle="2026",
        version_number=2,
        title="V2",
    )
    r1 = Requirement(
        id="r-ev-1",
        scholarship_version_id="v-ev-1",
        type="cgpa",
        operator="gte",
        value=3.5,
    )
    r2 = Requirement(
        id="r-ev-2",
        scholarship_version_id="v-ev-2",
        type="cgpa",
        operator="gte",
        value=3.8,
    )
    db_session.add_all([sch, v1, v2, r1, r2])
    db_session.commit()

    # EvidenceCheck linking v1 with r2 (which belongs to v2) must fail composite FK
    mismatched_ev = EvidenceCheck(
        id="ev-mismatch",
        scholarship_version_id="v-ev-1",
        requirement_id="r-ev-2",
        jev_label="Supported",
        probabilities={"Supported": 1.0},
        confidence=1.0,
    )
    db_session.add(mismatched_ev)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


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


def test_alembic_upgrade_empty_and_populated_database(tmp_path: Path):
    """
    Verifies Alembic migrations 0001 -> 0002 on:
    1. An empty database.
    2. A populated database with legacy student_profiles and student_applications.
    Also verifies the existence of all 10 required indexes in the database catalog.
    """
    repo_root = Path(__file__).resolve().parent.parent
    alembic_ini = repo_root / "alembic.ini"
    alembic_dir = repo_root / "alembic"

    # Part 1: Empty database upgrade
    empty_db = tmp_path / "empty_mig.db"
    cfg_empty = Config(str(alembic_ini))
    cfg_empty.set_main_option("sqlalchemy.url", f"sqlite:///{empty_db.as_posix()}")
    cfg_empty.set_main_option("script_location", str(alembic_dir))

    command.upgrade(cfg_empty, "0001_initial_schema")
    command.upgrade(cfg_empty, "head")

    # Verify all 10 required indexes exist in the catalog
    engine_empty = create_engine(f"sqlite:///{empty_db.as_posix()}")
    inspector = inspect(engine_empty)

    table_indexes: dict[str, set[str]] = {}
    for table_name in inspector.get_table_names():
        table_indexes[table_name] = {idx["name"] for idx in inspector.get_indexes(table_name)}

    required_indexes = [
        ("reminders", "ix_reminders_application_id"),
        ("retrievals", "ix_retrievals_retrieved_at"),
        ("scholarships", "ix_scholarships_source_id"),
        ("scholarships", "ix_scholarships_status"),
        ("scholarships", "ix_scholarships_freshness"),
        ("scholarship_versions", "ix_scholarship_versions_retrieval_id"),
        ("scholarship_versions", "ix_scholarship_versions_approved_by"),
        ("evidence_checks", "ix_evidence_checks_retrieval_id"),
        ("document_checklist_items", "ix_document_checklist_items_required_document_id"),
        ("interviews", "ix_interviews_status"),
    ]

    for tbl, idx_name in required_indexes:
        assert tbl in table_indexes, f"Table {tbl} not found in catalog"
        assert idx_name in table_indexes[tbl], (
            f"Index {idx_name} not found on table {tbl} in catalog"
        )

    # Part 2: Populated database upgrade
    pop_db = tmp_path / "populated_mig.db"
    cfg_pop = Config(str(alembic_ini))
    cfg_pop.set_main_option("sqlalchemy.url", f"sqlite:///{pop_db.as_posix()}")
    cfg_pop.set_main_option("script_location", str(alembic_dir))

    # Step A: Upgrade to 0001
    command.upgrade(cfg_pop, "0001_initial_schema")

    # Step B: Populate 0001 tables
    engine_pop = create_engine(f"sqlite:///{pop_db.as_posix()}")
    with engine_pop.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO student_profiles ("
                "  id, user_id, education_level, citizenship, household_income, cgpa"
                ") VALUES ("
                "  'prof-valid', 'usr-alice', 'Undergraduate', 'Malaysian', 5000.0, 3.9"
                "), ("
                "  'prof-orphan', '', 'Undergraduate', 'Malaysian', 6000.0, 3.8"
                ")"
            )
        )
        conn.execute(
            text(
                "INSERT INTO scholarships ("
                "  id, title, provider, official_portal_url, status, freshness"
                ") VALUES ("
                "  'sch-legacy-1', 'Legacy Scholarship', 'Legacy Provider', "
                "  'https://legacy.my', 'open', 'fresh'"
                ")"
            )
        )
        conn.execute(
            text(
                "INSERT INTO student_applications ("
                "  id, student_id, scholarship_id, stage, portal_submission_reference, notes"
                ") VALUES ("
                "  'app-leg-1', 'usr-alice', 'sch-legacy-1', 'drafting', 'REF-OLD-123', 'Old note'"
                "), ("
                "  'app-leg-dup', 'usr-alice', 'sch-legacy-1', 'drafting', 'REF-DUP', 'Duplicate'"
                "), ("
                "  'app-leg-orphan', 'usr-nonexistent', "
                "  'sch-legacy-1', 'submitted', 'REF-ORPH', 'No parent'"
                ")"
            )
        )

    # Step C: Upgrade to head (0002)
    command.upgrade(cfg_pop, "head")

    # Step D: Verify migrated data
    with engine_pop.begin() as conn:
        # 1. Verified users backfilled
        users = conn.execute(
            text("SELECT id, email, is_verified FROM users WHERE id = 'usr-alice'")
        ).fetchone()
        assert users is not None
        assert users[0] == "usr-alice"
        assert bool(users[2]) is True

        # 2. Orphan profile deleted; valid profile retained
        profiles = conn.execute(text("SELECT id, user_id FROM student_profiles")).fetchall()
        assert len(profiles) == 1
        assert profiles[0][0] == "prof-valid"
        assert profiles[0][1] == "usr-alice"

        # 3. Legacy applications transferred with stage mapping and reference mapping
        migrated_apps = conn.execute(
            text(
                "SELECT id, student_id, scholarship_id, stage, "
                "submission_reference, notes FROM applications"
            )
        ).fetchall()
        assert len(migrated_apps) == 1
        assert migrated_apps[0][0] == "app-leg-1"
        assert migrated_apps[0][1] == "usr-alice"
        assert migrated_apps[0][2] == "sch-legacy-1"
        assert migrated_apps[0][3] == "Preparing"
        assert migrated_apps[0][4] == "REF-OLD-123"
        assert migrated_apps[0][5] == "Old note"

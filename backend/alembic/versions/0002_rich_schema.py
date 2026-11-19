"""Comprehensive database schema migration

Revision ID: 0002_rich_schema
Revises: 0001_initial_schema
Create Date: 2026-11-19 16:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_rich_schema"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_tables = set(insp.get_table_names())

    # 1. Users
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False, server_default=""),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="student"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)

    # 2. Sources
    op.create_table(
        "sources",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("base_url", sa.String(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("schedule", sa.String(), nullable=False, server_default="0 0 * * *"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_retrieved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sources_name"), "sources", ["name"], unique=False)
    op.create_index(op.f("ix_sources_is_active"), "sources", ["is_active"], unique=False)

    # 3. Backfill verified users for student_profiles & Alter Student Profiles
    # Backfill verified owners (is_verified=true) for existing profiles before adding FK.
    # Safe handling: delete orphan profiles whose owners cannot be resolved without fake users.
    if "student_profiles" in existing_tables:
        profile_rows = bind.execute(sa.text("SELECT id, user_id FROM student_profiles")).fetchall()
        for p_id, u_id in profile_rows:
            clean_uid = str(u_id).strip() if u_id else ""
            if not clean_uid:
                # Safe handling policy: delete orphan profile without resolvable owner
                bind.execute(
                    sa.text("DELETE FROM student_profiles WHERE id = :id"),
                    {"id": p_id},
                )
            else:
                user_exists = bind.execute(
                    sa.text("SELECT id FROM users WHERE id = :user_id"),
                    {"user_id": clean_uid},
                ).first()
                if not user_exists:
                    # Backfill verified owner
                    bind.execute(
                        sa.text(
                            "INSERT INTO users ("
                            "  id, email, hashed_password, full_name, role, "
                            "  is_active, is_verified, created_at, updated_at"
                            ") VALUES ("
                            "  :id, :email, '', :full_name, 'student', "
                            "  :is_active, :is_verified, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP"
                            ")"
                        ),
                        {
                            "id": clean_uid,
                            "email": f"{clean_uid}@scholarpal.my",
                            "full_name": f"Student {clean_uid}",
                            "is_active": True,
                            "is_verified": True,
                        },
                    )
                else:
                    bind.execute(
                        sa.text("UPDATE users SET is_verified = :is_verified WHERE id = :user_id"),
                        {"user_id": clean_uid, "is_verified": True},
                    )

    with op.batch_alter_table("student_profiles") as batch_op:
        batch_op.add_column(sa.Column("study_level", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("nationality", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("academic_results", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("field_of_study", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("intended_field", sa.String(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            )
        )
        batch_op.create_foreign_key(
            "fk_student_profiles_user_id",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # 4. Retrievals & Processing Claims
    op.create_table(
        "retrievals",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("source_id", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("http_status_code", sa.Integer(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column(
            "retrieved_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_retrievals_source_id"), "retrievals", ["source_id"], unique=False)
    op.create_index(op.f("ix_retrievals_url"), "retrievals", ["url"], unique=False)
    op.create_index(op.f("ix_retrievals_status"), "retrievals", ["status"], unique=False)
    op.create_index(
        op.f("ix_retrievals_content_hash"), "retrievals", ["content_hash"], unique=False
    )
    op.create_index(
        op.f("ix_retrievals_retrieved_at"), "retrievals", ["retrieved_at"], unique=False
    )
    op.create_index(
        "ix_retrievals_source_url_hash",
        "retrievals",
        ["source_id", "url", "content_hash"],
        unique=False,
    )

    op.create_table(
        "retrieval_processing_claims",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("source_id", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "claimed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_id",
            "url",
            "content_hash",
            name="uq_retrieval_processing_claims",
        ),
    )
    op.create_index(
        op.f("ix_retrieval_processing_claims_source_id"),
        "retrieval_processing_claims",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_retrieval_processing_claims_url"),
        "retrieval_processing_claims",
        ["url"],
        unique=False,
    )
    op.create_index(
        op.f("ix_retrieval_processing_claims_content_hash"),
        "retrieval_processing_claims",
        ["content_hash"],
        unique=False,
    )

    # 5. Alter Scholarships (add source_id, timestamps, and indexes)
    with op.batch_alter_table("scholarships") as batch_op:
        batch_op.add_column(sa.Column("source_id", sa.String(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            )
        )
        batch_op.create_foreign_key(
            "fk_scholarships_source_id",
            "sources",
            ["source_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index(op.f("ix_scholarships_source_id"), ["source_id"], unique=False)
        batch_op.create_index(op.f("ix_scholarships_status"), ["status"], unique=False)
        batch_op.create_index(op.f("ix_scholarships_freshness"), ["freshness"], unique=False)

    # 6. Scholarship Versions
    op.create_table(
        "scholarship_versions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("scholarship_id", sa.String(), nullable=False),
        sa.Column("retrieval_id", sa.String(), nullable=True),
        sa.Column("application_cycle", sa.String(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("coverage_details", sa.JSON(), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("raw_extracted_data", sa.JSON(), nullable=True),
        sa.Column("approved_by", sa.String(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["scholarship_id"], ["scholarships.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["retrieval_id"], ["retrievals.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "scholarship_id",
            "application_cycle",
            "version_number",
            name="uq_scholarship_cycle_version",
        ),
    )
    op.create_index(
        op.f("ix_scholarship_versions_scholarship_id"),
        "scholarship_versions",
        ["scholarship_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_scholarship_versions_retrieval_id"),
        "scholarship_versions",
        ["retrieval_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_scholarship_versions_application_cycle"),
        "scholarship_versions",
        ["application_cycle"],
        unique=False,
    )
    op.create_index(
        op.f("ix_scholarship_versions_status"),
        "scholarship_versions",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_scholarship_versions_approved_by"),
        "scholarship_versions",
        ["approved_by"],
        unique=False,
    )

    # 7. Requirements
    op.create_table(
        "requirements",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("scholarship_version_id", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("operator", sa.String(), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("is_mandatory", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("source_excerpt", sa.Text(), nullable=True),
        sa.Column("is_subjective", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["scholarship_version_id"],
            ["scholarship_versions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "scholarship_version_id",
            "id",
            name="uq_requirements_version_id",
        ),
    )
    op.create_index(
        op.f("ix_requirements_scholarship_version_id"),
        "requirements",
        ["scholarship_version_id"],
        unique=False,
    )
    op.create_index(op.f("ix_requirements_type"), "requirements", ["type"], unique=False)
    op.create_index(
        op.f("ix_requirements_is_mandatory"),
        "requirements",
        ["is_mandatory"],
        unique=False,
    )

    # 8. Required Documents
    op.create_table(
        "required_documents",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("scholarship_version_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_mandatory", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("format_instructions", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["scholarship_version_id"],
            ["scholarship_versions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_required_documents_scholarship_version_id"),
        "required_documents",
        ["scholarship_version_id"],
        unique=False,
    )

    # 9. Evidence Checks (enforcing version-requirement pairing)
    op.create_table(
        "evidence_checks",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("scholarship_version_id", sa.String(), nullable=False),
        sa.Column("requirement_id", sa.String(), nullable=True),
        sa.Column("retrieval_id", sa.String(), nullable=True),
        sa.Column("jev_label", sa.String(), nullable=False),
        sa.Column("probabilities", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence_excerpt", sa.Text(), nullable=True),
        sa.Column("admin_verdict", sa.String(), nullable=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["scholarship_version_id"],
            ["scholarship_versions.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["scholarship_version_id", "requirement_id"],
            ["requirements.scholarship_version_id", "requirements.id"],
            ondelete="CASCADE",
            name="fk_evidence_checks_version_requirement",
        ),
        sa.ForeignKeyConstraint(["retrieval_id"], ["retrievals.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "scholarship_version_id",
            "requirement_id",
            name="uq_evidence_checks_version_req",
        ),
    )
    op.create_index(
        op.f("ix_evidence_checks_scholarship_version_id"),
        "evidence_checks",
        ["scholarship_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_evidence_checks_requirement_id"),
        "evidence_checks",
        ["requirement_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_evidence_checks_retrieval_id"),
        "evidence_checks",
        ["retrieval_id"],
        unique=False,
    )

    # 10. Applications & Data Transfer from student_applications
    op.create_table(
        "applications",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("student_id", sa.String(), nullable=False),
        sa.Column("scholarship_id", sa.String(), nullable=False),
        sa.Column("stage", sa.String(), nullable=False, server_default="Saved"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submission_reference", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scholarship_id"], ["scholarships.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_applications_student_id"), "applications", ["student_id"], unique=False
    )
    op.create_index(
        op.f("ix_applications_scholarship_id"),
        "applications",
        ["scholarship_id"],
        unique=False,
    )
    op.create_index(op.f("ix_applications_stage"), "applications", ["stage"], unique=False)
    op.create_index(
        "uq_applications_active_student_scholarship",
        "applications",
        ["student_id", "scholarship_id"],
        unique=True,
        postgresql_where=sa.text("stage != 'Withdrawn'"),
        sqlite_where=sa.text("stage != 'Withdrawn'"),
    )

    if "student_applications" in existing_tables:
        legacy_apps = bind.execute(
            sa.text(
                "SELECT id, student_id, scholarship_id, stage, submitted_at, "
                "portal_submission_reference, notes FROM student_applications"
            )
        ).fetchall()
        seen_pairs: set[tuple[str, str]] = set()
        for l_id, s_id, sch_id, stage, sub_at, ref, notes in legacy_apps:
            # Validate parent existence
            v_user = bind.execute(
                sa.text("SELECT id FROM users WHERE id = :u"), {"u": s_id}
            ).first()
            v_sch = bind.execute(
                sa.text("SELECT id FROM scholarships WHERE id = :s"), {"s": sch_id}
            ).first()
            if not v_user or not v_sch:
                continue

            mapped_stage = "Preparing" if stage == "drafting" else stage
            valid_stages = {
                "Saved",
                "Preparing",
                "Submitted",
                "Interview",
                "Offered",
                "Unsuccessful",
                "Withdrawn",
            }
            if mapped_stage not in valid_stages:
                mapped_stage = "Preparing"

            pair = (s_id, sch_id)
            if mapped_stage != "Withdrawn":
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)

            bind.execute(
                sa.text(
                    "INSERT INTO applications ("
                    "  id, student_id, scholarship_id, stage, submitted_at, "
                    "  submission_reference, notes, created_at, updated_at"
                    ") VALUES ("
                    "  :id, :student_id, :scholarship_id, :stage, :submitted_at, "
                    "  :ref, :notes, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP"
                    ")"
                ),
                {
                    "id": l_id,
                    "student_id": s_id,
                    "scholarship_id": sch_id,
                    "stage": mapped_stage,
                    "submitted_at": sub_at,
                    "ref": ref,
                    "notes": notes,
                },
            )
        op.drop_table("student_applications")

    # 11. Application Tasks
    op.create_table(
        "application_tasks",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("application_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("task_key", sa.String(), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("application_id", "task_key", name="uq_application_tasks_app_key"),
    )
    op.create_index(
        op.f("ix_application_tasks_application_id"),
        "application_tasks",
        ["application_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_application_tasks_task_key"),
        "application_tasks",
        ["task_key"],
        unique=False,
    )
    op.create_index(
        op.f("ix_application_tasks_is_completed"),
        "application_tasks",
        ["is_completed"],
        unique=False,
    )

    # 12. Document Checklist Items
    op.create_table(
        "document_checklist_items",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("application_id", sa.String(), nullable=False),
        sa.Column("required_document_id", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=True),
        sa.Column("file_name", sa.String(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["required_document_id"], ["required_documents.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "application_id",
            "required_document_id",
            name="uq_doc_checklist_app_doc",
        ),
    )
    op.create_index(
        op.f("ix_document_checklist_items_application_id"),
        "document_checklist_items",
        ["application_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_checklist_items_required_document_id"),
        "document_checklist_items",
        ["required_document_id"],
        unique=False,
    )

    # 13. Interviews
    op.create_table(
        "interviews",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("application_id", sa.String(), nullable=False),
        sa.Column("round_name", sa.String(), nullable=False, server_default="First Round"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location_or_url", sa.String(), nullable=True),
        sa.Column("format", sa.String(), nullable=False, server_default="in-person"),
        sa.Column("status", sa.String(), nullable=False, server_default="scheduled"),
        sa.Column("feedback_or_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_interviews_application_id"), "interviews", ["application_id"], unique=False
    )
    op.create_index(
        op.f("ix_interviews_scheduled_at"), "interviews", ["scheduled_at"], unique=False
    )
    op.create_index(op.f("ix_interviews_status"), "interviews", ["status"], unique=False)

    # 14. Award Offers (retaining single unique index on application_id)
    op.create_table(
        "award_offers",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("application_id", sa.String(), nullable=False),
        sa.Column("offer_amount", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="MYR"),
        sa.Column("coverage_terms", sa.JSON(), nullable=True),
        sa.Column("bond_duration_years", sa.Integer(), nullable=True),
        sa.Column("response_deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision", sa.String(), nullable=False, server_default="pending"),
        sa.Column("decision_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_award_offers_application_id"), "award_offers", ["application_id"], unique=True
    )
    op.create_index(op.f("ix_award_offers_decision"), "award_offers", ["decision"], unique=False)

    # 15. Reminders
    op.create_table(
        "reminders",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("application_id", sa.String(), nullable=True),
        sa.Column("task_id", sa.String(), nullable=True),
        sa.Column("interview_id", sa.String(), nullable=True),
        sa.Column("remind_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("is_sent", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["application_tasks.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reminders_user_id"), "reminders", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_reminders_application_id"), "reminders", ["application_id"], unique=False
    )
    op.create_index(op.f("ix_reminders_remind_at"), "reminders", ["remind_at"], unique=False)
    op.create_index(op.f("ix_reminders_is_sent"), "reminders", ["is_sent"], unique=False)

    # 16. Notifications
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("notification_type", sa.String(), nullable=False, server_default="general"),
        sa.Column("reference_url", sa.String(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)
    op.create_index(op.f("ix_notifications_is_read"), "notifications", ["is_read"], unique=False)
    op.create_index(
        op.f("ix_notifications_notification_type"),
        "notifications",
        ["notification_type"],
        unique=False,
    )

    # 17. Audit Log
    op.create_table(
        "audit_log",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("actor_id", sa.String(), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=False),
        sa.Column("changes", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_log_actor_id"), "audit_log", ["actor_id"], unique=False)
    op.create_index(op.f("ix_audit_log_action"), "audit_log", ["action"], unique=False)
    op.create_index(op.f("ix_audit_log_entity_type"), "audit_log", ["entity_type"], unique=False)
    op.create_index(op.f("ix_audit_log_entity_id"), "audit_log", ["entity_id"], unique=False)
    op.create_index(op.f("ix_audit_log_timestamp"), "audit_log", ["timestamp"], unique=False)


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("notifications")
    op.drop_table("reminders")
    op.drop_table("award_offers")
    op.drop_table("interviews")
    op.drop_table("document_checklist_items")
    op.drop_table("application_tasks")

    # Recreate student_applications if dropping applications
    op.create_table(
        "student_applications",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("student_id", sa.String(), nullable=False),
        sa.Column("scholarship_id", sa.String(), nullable=False),
        sa.Column("stage", sa.String(), nullable=False, server_default="drafting"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("portal_submission_reference", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_student_applications_student_id"),
        "student_applications",
        ["student_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_student_applications_scholarship_id"),
        "student_applications",
        ["scholarship_id"],
        unique=False,
    )

    op.drop_table("applications")
    op.drop_table("evidence_checks")
    op.drop_table("required_documents")
    op.drop_table("requirements")
    op.drop_table("scholarship_versions")

    with op.batch_alter_table("scholarships") as batch_op:
        batch_op.drop_index(op.f("ix_scholarships_freshness"))
        batch_op.drop_index(op.f("ix_scholarships_status"))
        batch_op.drop_index(op.f("ix_scholarships_source_id"))
        batch_op.drop_constraint("fk_scholarships_source_id", type_="foreignkey")
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")
        batch_op.drop_column("source_id")

    op.drop_table("retrieval_processing_claims")
    op.drop_table("retrievals")

    with op.batch_alter_table("student_profiles") as batch_op:
        batch_op.drop_constraint("fk_student_profiles_user_id", type_="foreignkey")
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")
        batch_op.drop_column("intended_field")
        batch_op.drop_column("field_of_study")
        batch_op.drop_column("academic_results")
        batch_op.drop_column("nationality")
        batch_op.drop_column("study_level")

    op.drop_table("sources")
    op.drop_table("users")

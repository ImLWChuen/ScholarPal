"""Initial schema for ScholarPal

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-11-19 15:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "student_profiles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("education_level", sa.String(), nullable=True),
        sa.Column("citizenship", sa.String(), nullable=True),
        sa.Column("state_of_origin", sa.String(), nullable=True),
        sa.Column("household_income", sa.Float(), nullable=True),
        sa.Column("cgpa", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_student_profiles_user_id"),
        "student_profiles",
        ["user_id"],
        unique=True,
    )

    op.create_table(
        "scholarships",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("official_portal_url", sa.String(), nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="open"),
        sa.Column("freshness", sa.String(), nullable=False, server_default="fresh"),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scholarships_title"), "scholarships", ["title"], unique=False)
    op.create_index(op.f("ix_scholarships_provider"), "scholarships", ["provider"], unique=False)

    op.create_table(
        "extraction_reviews",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("scholarship_id", sa.String(), nullable=False),
        sa.Column("source_url", sa.String(), nullable=False),
        sa.Column("extracted_data", sa.JSON(), nullable=False),
        sa.Column("jev_evidence_score", sa.Float(), nullable=True),
        sa.Column("jev_evidence_verdict", sa.String(), nullable=True),
        sa.Column(
            "review_status",
            sa.String(),
            nullable=False,
            server_default="pending_review",
        ),
        sa.Column("admin_notes", sa.String(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_extraction_reviews_scholarship_id"),
        "extraction_reviews",
        ["scholarship_id"],
        unique=False,
    )

    op.create_table(
        "eligibility_rules",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("scholarship_id", sa.String(), nullable=False),
        sa.Column("criterion_code", sa.String(), nullable=False),
        sa.Column("rule_type", sa.String(), nullable=False),
        sa.Column("rule_parameters", sa.JSON(), nullable=False),
        sa.Column(
            "is_mandatory",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_eligibility_rules_scholarship_id"),
        "eligibility_rules",
        ["scholarship_id"],
        unique=False,
    )

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

    op.create_table(
        "comparison_sets",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("student_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("scholarship_ids", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_comparison_sets_student_id"),
        "comparison_sets",
        ["student_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_comparison_sets_student_id"), table_name="comparison_sets")
    op.drop_table("comparison_sets")
    op.drop_index(
        op.f("ix_student_applications_scholarship_id"),
        table_name="student_applications",
    )
    op.drop_index(
        op.f("ix_student_applications_student_id"),
        table_name="student_applications",
    )
    op.drop_table("student_applications")
    op.drop_index(
        op.f("ix_eligibility_rules_scholarship_id"),
        table_name="eligibility_rules",
    )
    op.drop_table("eligibility_rules")
    op.drop_index(
        op.f("ix_extraction_reviews_scholarship_id"),
        table_name="extraction_reviews",
    )
    op.drop_table("extraction_reviews")
    op.drop_index(op.f("ix_scholarships_provider"), table_name="scholarships")
    op.drop_index(op.f("ix_scholarships_title"), table_name="scholarships")
    op.drop_table("scholarships")
    op.drop_index(op.f("ix_student_profiles_user_id"), table_name="student_profiles")
    op.drop_table("student_profiles")

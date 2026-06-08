"""filters and question bank

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-08 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # New filter fields on candidate_profiles
    op.add_column("candidate_profiles", sa.Column("company_blacklist", postgresql.ARRAY(sa.String), nullable=True))
    op.add_column("candidate_profiles", sa.Column("company_whitelist", postgresql.ARRAY(sa.String), nullable=True))
    op.add_column("candidate_profiles", sa.Column("title_keyword_blacklist", postgresql.ARRAY(sa.String), nullable=True))
    op.add_column("candidate_profiles", sa.Column("min_salary", sa.Integer, nullable=True))

    # Outcome tracking on applications
    op.add_column("applications", sa.Column("outcome", sa.String(30), nullable=True))
    op.add_column("applications", sa.Column("interview_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("applications", sa.Column("outcome_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("applications", sa.Column("feedback", sa.Text, nullable=True))

    # Question bank table
    op.create_table(
        "question_bank",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_question_bank_profile_id", "question_bank", ["profile_id"])


def downgrade() -> None:
    op.drop_index("ix_question_bank_profile_id", "question_bank")
    op.drop_table("question_bank")
    op.drop_column("applications", "feedback")
    op.drop_column("applications", "outcome_date")
    op.drop_column("applications", "interview_date")
    op.drop_column("applications", "outcome")
    op.drop_column("candidate_profiles", "min_salary")
    op.drop_column("candidate_profiles", "title_keyword_blacklist")
    op.drop_column("candidate_profiles", "company_whitelist")
    op.drop_column("candidate_profiles", "company_blacklist")

"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "candidate_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("full_name", sa.Text, nullable=False),
        sa.Column("email", sa.Text),
        sa.Column("phone", sa.Text),
        sa.Column("resume_text", sa.Text),
        sa.Column("resume_filename", sa.Text),
        sa.Column("target_titles", postgresql.ARRAY(sa.String)),
        sa.Column("target_locations", postgresql.ARRAY(sa.String)),
        sa.Column("skills", postgresql.ARRAY(sa.String)),
        sa.Column("years_exp", sa.Integer),
        sa.Column("story", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("external_id", sa.String(16), nullable=False, unique=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("company", sa.Text, nullable=False),
        sa.Column("location", sa.Text),
        sa.Column("description", sa.Text),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("posted_date", sa.Date),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("match_score", sa.SmallInteger),
        sa.Column("score_reasoning", sa.Text),
        sa.Column("cover_letter", sa.Text),
        sa.Column("is_remote", sa.Boolean, server_default="false"),
        sa.Column("salary_range", sa.Text),
    )
    op.create_index("ix_jobs_external_id", "jobs", ["external_id"])

    op.create_table(
        "applications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidate_profiles.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="saved"),
        sa.Column("applied_at", sa.DateTime(timezone=True)),
        sa.Column("cover_letter_used", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "scrape_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidate_profiles.id"), nullable=False),
        sa.Column("cron_expression", sa.Text, nullable=False),
        sa.Column("portals", postgresql.ARRAY(sa.String)),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("last_run_at", sa.DateTime(timezone=True)),
        sa.Column("next_run_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "scrape_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("schedule_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("scrape_schedules.id")),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20), server_default="running"),
        sa.Column("jobs_found", sa.Integer, server_default="0"),
        sa.Column("jobs_new", sa.Integer, server_default="0"),
        sa.Column("error_message", sa.Text),
    )

    op.create_table(
        "outreach_contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text),
        sa.Column("title", sa.Text),
        sa.Column("email", sa.Text),
        sa.Column("linkedin_url", sa.Text),
        sa.Column("source", sa.Text),
        sa.Column("email_sent", sa.Boolean, server_default="false"),
        sa.Column("email_sent_at", sa.DateTime(timezone=True)),
        sa.Column("email_subject", sa.Text),
        sa.Column("email_body", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("outreach_contacts")
    op.drop_table("scrape_logs")
    op.drop_table("scrape_schedules")
    op.drop_table("applications")
    op.drop_index("ix_jobs_external_id", "jobs")
    op.drop_table("jobs")
    op.drop_table("candidate_profiles")

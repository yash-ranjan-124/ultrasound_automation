"""Create the persistent imaging study catalog."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261002_01"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "medvision_studies",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("filename", sa.Text(), nullable=False),
        sa.Column("study_type", sa.String(length=16), nullable=False),
        sa.Column("modality", sa.String(length=24), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index(
        "ix_medvision_studies_created_at",
        "medvision_studies",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_medvision_studies_created_at", table_name="medvision_studies")
    op.drop_table("medvision_studies")

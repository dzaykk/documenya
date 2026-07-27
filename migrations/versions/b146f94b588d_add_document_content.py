"""Add document content

Revision ID: b146f94b588d
Revises: edb11c9e3e0d
"""

from alembic import op
import sqlalchemy as sa

revision = "b146f94b588d"
down_revision = "edb11c9e3e0d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column(
            "content",
            sa.Text(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "documents",
        "content",
    )
"""Add document processing error"""

from alembic import op
import sqlalchemy as sa

revision = "ad7315ba7350"
down_revision = "9d0b176016c1"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.add_column(
        "documents",
        sa.Column(
            "processing_error",
            sa.Text(),
            nullable=True,
        ),
    )


def downgrade() -> None:

    op.drop_column(
        "documents",
        "processing_error",
    )
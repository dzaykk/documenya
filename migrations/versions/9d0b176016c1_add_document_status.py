"""Add document status"""

from alembic import op
import sqlalchemy as sa

revision = "9d0b176016c1"
down_revision = "b146f94b588d"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.add_column(
        "documents",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE documents
        SET status = 'completed'
        WHERE status IS NULL
        """
    )

    op.alter_column(
        "documents",
        "status",
        nullable=False,
    )


def downgrade() -> None:

    op.drop_column(
        "documents",
        "status",
    )
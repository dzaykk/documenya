"""add token version"""

from alembic import op
import sqlalchemy as sa

revision: str = "c05abde52cf5"
down_revision = "ad7315ba7350"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.add_column(
        "users",
        sa.Column(
            "token_version",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )


def downgrade() -> None:

    op.drop_column(
        "users",
        "token_version",
    )
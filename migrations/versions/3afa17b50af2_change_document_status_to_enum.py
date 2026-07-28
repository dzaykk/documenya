"""change document status to enum"""

from alembic import op
import sqlalchemy as sa


revision: str = "3afa17b50af2"
down_revision = "c05abde52cf5"
branch_labels = None
depends_on = None


document_status_enum = sa.Enum(
    "processing",
    "completed",
    "failed",
    name="document_status",
)


def upgrade() -> None:

    document_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.alter_column(
        "documents",
        "status",
        existing_type=sa.VARCHAR(length=20),
        type_=document_status_enum,
        postgresql_using=(
            "status::text::document_status"
        ),
        existing_nullable=False,
    )


def downgrade() -> None:

    op.alter_column(
        "documents",
        "status",
        existing_type=document_status_enum,
        type_=sa.VARCHAR(length=20),
        postgresql_using=(
            "status::text"
        ),
        existing_nullable=False,
    )

    document_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )
"""add document processing error

Revision ID: ad7315ba7350
Revises: 9d0b176016c1
Create Date: 2026-07-19 18:35:58.493804

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ad7315ba7350"
down_revision: Union[str, Sequence[str], None] = "9d0b176016c1"
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
"""add document chunks"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "c250e761e323"
down_revision: str | None = "3afa17b50af2"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "document_chunks",

        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
        ),

        sa.Column(
            "document_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "owner_id",
            sa.Integer(), 
            nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "chunk_index",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "page",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "section",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "vector_id",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "id",
        ),

        sa.UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunk_index",
        ),
    )


    op.create_index(
        "ix_document_chunks_document_id",
        "document_chunks",
        ["document_id"],
    )

    op.create_index(
        "ix_document_chunks_owner_id",
        "document_chunks",
        ["owner_id"],
    )

    op.create_index(
        "ix_document_chunks_vector_id",
        "document_chunks",
        ["vector_id"],
    )


def downgrade() -> None:

    op.drop_index(
        "ix_document_chunks_vector_id",
        table_name="document_chunks",
    )

    op.drop_index(
        "ix_document_chunks_owner_id",
        table_name="document_chunks",
    )

    op.drop_index(
        "ix_document_chunks_document_id",
        table_name="document_chunks",
    )

    op.drop_table(
        "document_chunks",
    )
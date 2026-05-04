"""add pgvector extension

Revision ID: 477011cd8bf7
Revises: 
Create Date: 2026-05-03 21:35:04.319721

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '477011cd8bf7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    """Downgrade schema."""
    # pgvector extension cannot be easily removed in production
    # but we can for development
    op.execute("DROP EXTENSION IF EXISTS vector")

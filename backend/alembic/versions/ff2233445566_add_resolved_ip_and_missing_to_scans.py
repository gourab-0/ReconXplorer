"""add resolved_ip and missing to scans

Revision ID: ff2233445566
Revises: ff1122334455
Create Date: 2026-02-16 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff2233445566'
down_revision: Union[str, Sequence[str], None] = 'ff1122334455'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use a raw SQL approach for Postgres to safely add columns if they don't exist
    op.execute("ALTER TABLE scans ADD COLUMN IF NOT EXISTS resolved_ip VARCHAR")
    op.execute("ALTER TABLE scans ADD COLUMN IF NOT EXISTS ai_summary TEXT")
    op.execute("ALTER TABLE scans ADD COLUMN IF NOT EXISTS ai_deep_summary TEXT")
    # Also ensuring others from older migrations that might have failed
    op.execute("ALTER TABLE scans ADD COLUMN IF NOT EXISTS progress INTEGER DEFAULT 0")
    op.execute("ALTER TABLE scans ADD COLUMN IF NOT EXISTS current_phase VARCHAR")
    op.execute("ALTER TABLE scans ADD COLUMN IF NOT EXISTS profile VARCHAR DEFAULT 'full'")


def downgrade() -> None:
    op.execute("ALTER TABLE scans DROP COLUMN IF EXISTS ai_deep_summary")
    op.execute("ALTER TABLE scans DROP COLUMN IF EXISTS ai_summary")
    op.execute("ALTER TABLE scans DROP COLUMN IF EXISTS resolved_ip")

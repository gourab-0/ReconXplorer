"""add account lockout and audit logs

Revision ID: ff3344556677
Revises: ff2233445566
Create Date: 2026-02-21 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ff3344556677'
down_revision: Union[str, Sequence[str], None] = 'ff2233445566'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add lockout fields to users
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE")
    
    # Create audit_logs table if it doesn't exist
    # Note: gen_random_uuid() requires pgcrypto extension, usually installed. 
    # If not, uuid_generate_v4() if uuid-ossp is installed.
    # Safe fallback: Let SQLAlchemy handle default if creating via ORM, but here in raw SQL:
    # We will assume gen_random_uuid() is available (Postgres 13+).
    op.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        admin_id UUID NOT NULL REFERENCES users(id),
        action VARCHAR NOT NULL,
        target_user VARCHAR,
        details VARCHAR,
        ip_address VARCHAR,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT now()
    )
    """)

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS audit_logs")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS locked_until")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS failed_login_attempts")

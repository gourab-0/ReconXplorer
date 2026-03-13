"""add refresh token store and ip tracking

Revision ID: ff4455667788
Revises: ff3344556677
Create Date: 2026-02-21 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'ff4455667788'
down_revision: Union[str, Sequence[str], None] = 'ff3344556677'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add last_login_ip to users
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_ip VARCHAR")
    
    # Create refresh_tokens table
    op.execute("""
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token_hash VARCHAR NOT NULL UNIQUE,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        is_revoked BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_refresh_tokens_token_hash ON refresh_tokens (token_hash)")

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS refresh_tokens")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS last_login_ip")

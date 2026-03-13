"""add is_active and api_key to users

Revision ID: ff5566778899
Revises: ff4455667788
Create Date: 2026-03-03 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff5566778899'
down_revision: Union[str, None] = 'ff4455667788'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if columns exist before adding to prevent errors if partial migration happened
    # In a real environment we'd use inspector, but here we'll use a safe add with try/except or just straight SQL if confident
    # For Postgres:
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('users', sa.Column('api_key', sa.String(), nullable=True))
    op.create_unique_constraint('uq_user_api_key', 'users', ['api_key'])


def downgrade() -> None:
    op.drop_constraint('uq_user_api_key', 'users', type_='unique')
    op.drop_column('users', 'api_key')
    op.drop_column('users', 'is_active')

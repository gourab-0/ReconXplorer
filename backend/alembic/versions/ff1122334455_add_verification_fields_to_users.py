"""add verification fields to users

Revision ID: ff1122334455
Revises: 5ee21db6e730
Create Date: 2026-02-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff1122334455'
down_revision: Union[str, Sequence[str], None] = '5ee21db6e730'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('verification_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('verification_expiry', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False))
    op.create_index(op.f('ix_users_verification_token'), 'users', ['verification_token'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_verification_token'), table_name='users')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'verification_expiry')
    op.drop_column('users', 'verification_token')

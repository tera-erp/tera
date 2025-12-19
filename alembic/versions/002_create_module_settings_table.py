"""Create module_settings table

Revision ID: 002_create_module_settings_table
Revises: 001_split_user_fullname
Create Date: 2025-12-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_create_module_settings_table'
down_revision: Union[str, None] = '001_split_user_fullname'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'module_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('module_id', sa.String(length=100), nullable=False, index=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('key', sa.String(length=200), nullable=False, index=True),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index(op.f('ix_module_settings_module_id'), 'module_settings', ['module_id'], unique=False)
    op.create_index(op.f('ix_module_settings_key'), 'module_settings', ['key'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_module_settings_key'), table_name='module_settings')
    op.drop_index(op.f('ix_module_settings_module_id'), table_name='module_settings')
    op.drop_table('module_settings')

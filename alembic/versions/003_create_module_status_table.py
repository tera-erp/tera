"""Create module_status table

Revision ID: 003_create_module_status_table
Revises: 002_create_module_settings_table
Create Date: 2025-12-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_create_module_status_table'
down_revision: Union[str, None] = '002_create_module_settings_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'module_status',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('module_id', sa.String(length=100), nullable=False, index=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('enabled_at', sa.DateTime(), nullable=True),
        sa.Column('enabled_by', sa.String(length=200), nullable=True),
        sa.Column('disabled_at', sa.DateTime(), nullable=True),
        sa.Column('disabled_by', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_module_status_module_id'), 'module_status', ['module_id'], unique=False)
    op.create_index(op.f('ix_module_status_company_id'), 'module_status', ['company_id'], unique=False)
    # Create unique constraint for module_id + company_id
    op.create_unique_constraint('uq_module_status_module_company', 'module_status', ['module_id', 'company_id'])


def downgrade() -> None:
    op.drop_constraint('uq_module_status_module_company', 'module_status', type_='unique')
    op.drop_index(op.f('ix_module_status_company_id'), table_name='module_status')
    op.drop_index(op.f('ix_module_status_module_id'), table_name='module_status')
    op.drop_table('module_status')

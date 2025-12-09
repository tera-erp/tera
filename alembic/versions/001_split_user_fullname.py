"""Split user full_name into first_name and last_name

Revision ID: 001_split_user_fullname
Revises:
Create Date: 2025-12-09 19:32:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_split_user_fullname'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns as nullable first
    op.add_column('users', sa.Column('first_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=100), nullable=True))

    # Migrate data from full_name to first_name and last_name
    # This uses a simple split on the first space
    op.execute("""
        UPDATE users
        SET
            first_name = SPLIT_PART(full_name, ' ', 1),
            last_name = CASE
                WHEN POSITION(' ' IN full_name) > 0
                THEN SUBSTRING(full_name FROM POSITION(' ' IN full_name) + 1)
                ELSE ''
            END
        WHERE full_name IS NOT NULL
    """)

    # Set default values for any NULL fields
    op.execute("UPDATE users SET first_name = 'Unknown' WHERE first_name IS NULL OR first_name = ''")
    op.execute("UPDATE users SET last_name = 'User' WHERE last_name IS NULL OR last_name = ''")

    # Make columns non-nullable
    op.alter_column('users', 'first_name', nullable=False)
    op.alter_column('users', 'last_name', nullable=False)

    # Drop the old full_name column
    op.drop_column('users', 'full_name')


def downgrade() -> None:
    # Add full_name column back
    op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=True))

    # Migrate data back
    op.execute("""
        UPDATE users
        SET full_name = first_name || ' ' || last_name
    """)

    # Make full_name non-nullable
    op.alter_column('users', 'full_name', nullable=False)

    # Drop the split columns
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')

"""add_reminder_to_tasks

Revision ID: 9bd681cd47e3
Revises: 6444e4e2d1cf
Create Date: 2025-03-25 10:11:43.699360

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9bd681cd47e3'
down_revision: Union[str, None] = '6444e4e2d1cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем колонку reminder
    op.add_column('tasks',
                  sa.Column('reminder', sa.DateTime(), nullable=True)
                  )


def downgrade() -> None:
    # Удаляем колонку reminder
    op.drop_column('tasks', 'reminder')

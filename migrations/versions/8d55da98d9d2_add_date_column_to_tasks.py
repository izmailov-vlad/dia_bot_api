"""add_date_column_to_tasks

Revision ID: 8d55da98d9d2
Revises: e6c7dc172ced
Create Date: 2025-04-26 21:11:42.653160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d55da98d9d2'
down_revision: Union[str, None] = 'e6c7dc172ced'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем колонку date
    op.add_column('tasks',
                  sa.Column('date', sa.Date(), nullable=False)
                  )


def downgrade() -> None:
    # Удаляем колонку date
    op.drop_column('tasks', 'date')

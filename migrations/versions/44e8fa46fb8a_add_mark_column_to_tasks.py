"""add_mark_column_to_tasks

Revision ID: 44e8fa46fb8a
Revises: 5f34fc31b840
Create Date: 2025-03-25 10:05:45.920064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44e8fa46fb8a'
down_revision: Union[str, None] = '5f34fc31b840'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем колонку mark
    op.add_column('tasks', sa.Column('mark', sa.String(), nullable=True))


def downgrade() -> None:
    # Удаляем колонку mark при откате
    op.drop_column('tasks', 'mark')

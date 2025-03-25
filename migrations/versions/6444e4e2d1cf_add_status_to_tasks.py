"""add_status_to_tasks

Revision ID: 6444e4e2d1cf
Revises: 44e8fa46fb8a
Create Date: 2025-03-25 10:08:32.274971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6444e4e2d1cf'
down_revision: Union[str, None] = '44e8fa46fb8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем enum тип
    task_status = sa.Enum('created', 'completed', name='taskstatus')
    task_status.create(op.get_bind())

    # Добавляем колонку status
    op.add_column(
        'tasks',
        sa.Column(
            'status',
            sa.Enum('created', 'completed', name='taskstatus'),
            nullable=False,
            server_default='created'
        )
    )


def downgrade() -> None:
    # Удаляем колонку status
    op.drop_column('tasks', 'status')

    # Удаляем enum тип
    sa.Enum(name='taskstatus').drop(op.get_bind())

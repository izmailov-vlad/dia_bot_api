"""create_table_tasks

Revision ID: 4a614d40c9da
Revises: 
Create Date: 2025-03-17 09:50:41.799061

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Enum


# revision identifiers, used by Alembic.
revision: str = '4a614d40c9da'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем enum типы
    task_status = sa.Enum(
        'planned',
        'in_progress',
        'completed',
        'cancelled',
        name='taskstatus',
    )
    task_priority = sa.Enum(
        'low',
        'medium',
        'high',
        'critical',
        name='taskpriority',
    )

    # Создаем таблицу tasks
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('priority', task_priority, nullable=True, default='low'),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('status', task_status, nullable=False, default='planned'),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Удаляем таблицу
    op.drop_table('tasks')

    # Удаляем enum типы
    op.execute('DROP TYPE taskstatus')
    op.execute('DROP TYPE taskpriority')

"""create_table_tasks

Revision ID: 4a614d40c9da
Revises: 
Create Date: 2025-03-17 09:50:41.799061

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a614d40c9da'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Создаем таблицу tasks
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
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
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('smart_tag_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['smart_tag_id'], ['smart_tags.id'])
    )

    # Создаем индексы для ускорения поиска по внешним ключам
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('ix_tasks_smart_tag_id', 'tasks', ['smart_tag_id'])


def downgrade() -> None:
    # Удаляем индексы
    op.drop_index('ix_tasks_smart_tag_id', table_name='tasks')
    op.drop_index('ix_tasks_user_id', table_name='tasks')

    # Удаляем таблицу
    op.drop_table('tasks')

"""create tasks table

Revision ID: 21bfa82316c0
Revises: b75676a2709e
Create Date: 2025-03-15 13:52:52.732870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21bfa82316c0'
down_revision: Union[str, None] = 'b75676a2709e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Создаем enum типы
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'critical', name='taskpriority'), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('planned', 'in_progress', 'completed', 'cancelled', name='taskstatus'), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('reminders', sa.JSON(), nullable=True),
        sa.Column('recurrence', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), server_onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Удаляем таблицу и enum типы
    op.drop_table('tasks')
    op.execute('DROP TYPE IF EXISTS taskpriority')
    op.execute('DROP TYPE IF EXISTS taskstatus')

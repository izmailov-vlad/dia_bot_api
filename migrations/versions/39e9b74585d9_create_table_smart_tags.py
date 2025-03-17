"""create_table_smart_tags

Revision ID: 39e9b74585d9
Revises: 4a614d40c9da
Create Date: 2025-03-17 09:54:20.951001

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39e9b74585d9'
down_revision: Union[str, None] = '4a614d40c9da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from alembic import op
import sqlalchemy as sa
from database.models.smart_tag_model import SmartTagPriority

def upgrade() -> None:
    op.create_table(
        'smart_tags',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('default_duration', sa.Integer(), default=60, nullable=False),
        sa.Column('priority', sa.Enum(SmartTagPriority), default=SmartTagPriority.MEDIUM, nullable=True),
        sa.Column('reminder', sa.Integer(), nullable=True),
        sa.Column('color', sa.String(), default="#FF5733", nullable=True),
        sa.Column('daily_limit', sa.Integer(), nullable=True),
        sa.Column('time_range_id', sa.String(), sa.ForeignKey('time_ranges.id'), nullable=True),
        sa.Column('recurrence_id', sa.String(), sa.ForeignKey('recurrences.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Создаем индекс для поиска по имени
    op.create_index('ix_smart_tags_name', 'smart_tags', ['name'])

def downgrade() -> None:
    # Удаляем индекс
    op.drop_index('ix_smart_tags_name')
    
    # Удаляем таблицу
    op.drop_table('smart_tags')
    
    # Удаляем enum
    op.execute('DROP TYPE IF EXISTS smarttagpriority')

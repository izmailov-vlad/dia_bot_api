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


def upgrade() -> None:
    op.create_table(
        'smart_tags',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text(
            'CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text(
            'CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )

    # Создаем индексы
    op.create_index('ix_smart_tags_name', 'smart_tags', ['name'])
    op.create_index('ix_smart_tags_user_id', 'smart_tags', ['user_id'])


def downgrade() -> None:
    # Удаляем индексы
    op.drop_index('ix_smart_tags_name')
    op.drop_index('ix_smart_tags_user_id')

    # Удаляем таблицу
    op.drop_table('smart_tags')

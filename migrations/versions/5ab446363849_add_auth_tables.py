"""add_auth_tables

Revision ID: 5ab446363849
Revises: 1b292dba0978
Create Date: 2025-03-21 09:47:48.216683

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ab446363849'
down_revision: Union[str, None] = '1b292dba0978'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Создаем таблицу refresh_tokens
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    
    # Создаем индекс для ускорения поиска по токенам
    op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'])
    
    # Создаем индекс для ускорения поиска по user_id
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])


def downgrade() -> None:
    # Удаляем индексы
    op.drop_index('ix_refresh_tokens_user_id', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_token', table_name='refresh_tokens')
    
    # Удаляем таблицу refresh_tokens
    op.drop_table('refresh_tokens')
    
    # Удаляем колонку password_hash из таблицы users
    op.drop_column('users', 'password_hash')
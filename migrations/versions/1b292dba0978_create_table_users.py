"""create_table_users

Revision ID: 1b292dba0978
Revises: 39e9b74585d9
Create Date: 2025-03-21 08:48:09.940924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b292dba0978'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем таблицу users
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('telegram_id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
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
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )

    # Создаем индекс для ускорения поиска по telegram_id
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'])

    # Создаем индекс для ускорения поиска по username
    op.create_index('ix_users_username', 'users', ['username'])


def downgrade() -> None:
    # Удаляем индексы
    op.drop_index('ix_users_username')
    op.drop_index('ix_users_telegram_id')

    # Удаляем таблицу
    op.drop_table('users')

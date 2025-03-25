"""add_priority_column_to_tasks

Revision ID: 5f34fc31b840
Revises: 5ab446363849
Create Date: 2025-03-24 09:39:19.709692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f34fc31b840'
down_revision: Union[str, None] = '4a614d40c9da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Определяем возможные значения для Enum
priority_values = ('1', '2', '3', '4')


def upgrade():
    # Добавляем колонку priority как целое число с ограничением CHECK
    op.add_column('tasks', sa.Column(
        'priority',
        sa.Integer(),
        server_default='1',  # Обратите внимание: server_default должен быть строкой
        nullable=False
    ))

    # Добавляем ограничение CHECK для эмуляции enum
    # Исправляем формирование строки для ограничения
    priority_check = f"priority IN {str(priority_values)}"
    op.create_check_constraint(
        'ck_tasks_priority_values',
        'tasks',
        priority_check
    )


def downgrade():
    # Удаляем ограничение CHECK
    # Примечание: В SQLite нельзя удалить ограничение без пересоздания таблицы,
    # поэтому этот код может не работать напрямую в SQLite
    op.drop_constraint('ck_tasks_priority_values', 'tasks', type_='check')

    # Удаляем колонку (это должно работать)
    op.drop_column('tasks', 'priority')

"""alter_tasks_make_start_time_nullable

Revision ID: 2ce5ac80ca5a
Revises: 8d55da98d9d2
Create Date: 2025-04-26 18:12:04.896440

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ce5ac80ca5a'
down_revision: Union[str, None] = '8d55da98d9d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Изменяем колонку start_time на nullable
    op.alter_column('tasks', 'start_time',
                    existing_type=sa.DateTime(),
                    nullable=True)


def downgrade() -> None:
    # Заполняем пустые значения start_time текущим временем
    op.execute(
        "UPDATE tasks SET start_time = CURRENT_TIMESTAMP WHERE start_time IS NULL")

    # Возвращаем колонку start_time в not nullable состояние
    op.alter_column('tasks', 'start_time',
                    existing_type=sa.DateTime(),
                    nullable=False)

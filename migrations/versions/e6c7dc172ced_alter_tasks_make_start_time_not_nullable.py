"""alter_tasks_make_start_time_not_nullable

Revision ID: e6c7dc172ced
Revises: 5649d603f087
Create Date: 2024-04-26 19:48:42.653160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6c7dc172ced'
down_revision: Union[str, None] = '5649d603f087'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Затем делаем колонку not nullable
    op.alter_column('tasks', 'start_time',
                    existing_type=sa.DateTime(),
                    nullable=False)


def downgrade() -> None:
    # Возвращаем колонку в nullable состояние
    op.alter_column('tasks', 'start_time',
                    existing_type=sa.DateTime(),
                    nullable=True)

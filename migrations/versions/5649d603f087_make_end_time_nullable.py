"""make_end_time_nullable

Revision ID: 5649d603f087
Revises: 9bd681cd47e3
Create Date: 2025-03-25 10:14:03.090543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5649d603f087'
down_revision: Union[str, None] = '9bd681cd47e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Изменяем колонку end_time на nullable
    op.alter_column('tasks', 'end_time',
        existing_type=sa.DateTime(),
        nullable=True
    )

def downgrade() -> None:
    # Возвращаем not null constraint
    op.alter_column('tasks', 'end_time',
        existing_type=sa.DateTime(),
        nullable=False
    )

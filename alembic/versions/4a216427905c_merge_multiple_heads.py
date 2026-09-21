"""merge multiple heads

Revision ID: 4a216427905c
Revises: 3980827cf050, 8b9c0d1e2f3a
Create Date: 2026-09-10 00:27:22.217526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a216427905c'
down_revision: Union[str, Sequence[str], None] = ('3980827cf050', '8b9c0d1e2f3a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

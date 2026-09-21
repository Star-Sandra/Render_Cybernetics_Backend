"""added two columns in the repository-visits

Revision ID: e8317d413041
Revises: 4a216427905c
Create Date: 2026-09-10 00:27:48.559795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8317d413041'
down_revision: Union[str, Sequence[str], None] = '4a216427905c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op: ix_reset_otps_user_id was never created since 7a1b2c3d4e5f
    is now a no-op — nothing to drop, desired end state already reached."""
    pass

def downgrade() -> None:
    pass
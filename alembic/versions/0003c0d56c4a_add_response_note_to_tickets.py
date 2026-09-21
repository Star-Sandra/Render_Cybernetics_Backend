"""add response_note to tickets

Revision ID: 0003c0d56c4a
Revises: ced87c5d7877
Create Date: 2026-09-02 09:29:35.146965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003c0d56c4a'
down_revision: Union[str, Sequence[str], None] = 'ced87c5d7877'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op: tickets.response_note and visit_logs.blood_sugar are now
    created directly in ced87c5d7877, which this migration now follows."""
    pass


def downgrade() -> None:
    pass
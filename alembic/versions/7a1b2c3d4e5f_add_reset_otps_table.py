"""add reset_otps table for password reset OTP flow

Revision ID: 7a1b2c3d4e5f
Revises: 0003c0d56c4a
Create Date: 2026-09-04 13:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '7a1b2c3d4e5f'
down_revision: Union[str, Sequence[str], None] = '0003c0d56c4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op: reset_otps is now created directly in ced87c5d7877."""
    pass


def downgrade() -> None:
    pass
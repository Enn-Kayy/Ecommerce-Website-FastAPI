"""add order relationship

Revision ID: d714e592839e
Revises: de7f908db0f8
Create Date: 2025-11-01 14:15:22.772665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd714e592839e'
down_revision: Union[str, Sequence[str], None] = 'de7f908db0f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

"""merge heads for building

Revision ID: bcf621ce4451
Revises: a1b2c3d4e5f6, aaaa_building_0001
Create Date: 2025-08-09 16:53:17.311455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bcf621ce4451'
down_revision = ('a1b2c3d4e5f6', 'aaaa_building_0001')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

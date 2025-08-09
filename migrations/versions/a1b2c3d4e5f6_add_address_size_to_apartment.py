"""Add missing address and size_sqm columns to apartment

Revision ID: a1b2c3d4e5f6
Revises: 5bab8952e54e
Create Date: 2025-08-08 19:40:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '5bab8952e54e'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    if 'apartment' in tables:
        cols = {c['name'] for c in inspector.get_columns('apartment')}
        if 'address' not in cols:
            op.add_column('apartment', sa.Column('address', sa.String(length=200), nullable=False, server_default=''))
        if 'size_sqm' not in cols:
            op.add_column('apartment', sa.Column('size_sqm', sa.Float(), nullable=False, server_default='0'))


def downgrade():
    # Safe drop if columns exist
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    if 'apartment' in tables:
        cols = {c['name'] for c in inspector.get_columns('apartment')}
        if 'size_sqm' in cols:
            op.drop_column('apartment', 'size_sqm')
        if 'address' in cols:
            op.drop_column('apartment', 'address')



"""add entry_type to consumption_data

Revision ID: 030da51516ae
Revises: c37155871e54
Create Date: 2025-04-01 10:37:03.405684

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '030da51516ae'
down_revision = 'c37155871e54'
branch_labels = None
depends_on = None


def upgrade():
    """Fix duplicate operations: ensure only missing index is created.

    Earlier revision c37155871e54 already added the 'entry_type' column.
    All base tables are created by prior revisions. This migration should be
    a no-op except for adding the composite index if it does not yet exist.
    """
    bind = op.get_bind()
    inspector = inspect(bind)
    if 'consumption_data' in inspector.get_table_names():
        existing_indexes = {idx['name'] for idx in inspector.get_indexes('consumption_data')}
        index_name = 'ix_consumption_data_apartment_cost_type_date'
        if index_name not in existing_indexes:
            op.create_index(index_name, 'consumption_data', ['apartment_id', 'cost_type_id', 'date'], unique=False)


def downgrade():
    # Only drop the index if present; leave base tables intact
    bind = op.get_bind()
    inspector = inspect(bind)
    if 'consumption_data' in inspector.get_table_names():
        existing_indexes = {idx['name'] for idx in inspector.get_indexes('consumption_data')}
        index_name = 'ix_consumption_data_apartment_cost_type_date'
        if index_name in existing_indexes:
            op.drop_index(index_name, table_name='consumption_data')

"""Expand core data models

Revision ID: 5bab8952e54e
Revises: 030da51516ae
Create Date: 2025-04-01 14:45:08.362015

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '5bab8952e54e'
down_revision = '030da51516ae'
branch_labels = None
depends_on = None


def upgrade():
    # Idempotente Erstellung: Nur anlegen, wenn Tabelle/Index noch nicht existiert
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if 'apartment' not in existing_tables:
        op.create_table('apartment',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('number', sa.String(length=50), nullable=False),
            sa.Column('address', sa.String(length=200), nullable=False),
            sa.Column('size_sqm', sa.Float(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('apartment', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_apartment_number'), ['number'], unique=True)
    else:
        # Tabelle existiert bereits (z. B. von einer älteren Migration); fehlende Spalten hinzufügen
        cols = {c['name'] for c in inspector.get_columns('apartment')}
        if 'address' not in cols:
            op.add_column('apartment', sa.Column('address', sa.String(length=200), nullable=True))
        if 'size_sqm' not in cols:
            op.add_column('apartment', sa.Column('size_sqm', sa.Float(), nullable=True))
        # Index sicherstellen
        existing_indexes = {idx['name'] for idx in inspector.get_indexes('apartment')}
        if 'ix_apartment_number' not in existing_indexes:
            with op.batch_alter_table('apartment', schema=None) as batch_op:
                batch_op.create_index(batch_op.f('ix_apartment_number'), ['number'], unique=True)

    if 'cost_type' not in existing_tables:
        op.create_table('cost_type',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('unit', sa.String(length=20), nullable=False),
            sa.Column('type', sa.String(length=20), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )

    if 'tenant' not in existing_tables:
        op.create_table('tenant',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('contact_info', sa.String(length=200), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    if 'apartment_share' not in existing_tables:
        op.create_table('apartment_share',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('apartment_id', sa.Integer(), nullable=False),
            sa.Column('cost_type_id', sa.Integer(), nullable=False),
            sa.Column('value', sa.Float(), nullable=False),
            sa.ForeignKeyConstraint(['apartment_id'], ['apartment.id'], ),
            sa.ForeignKeyConstraint(['cost_type_id'], ['cost_type.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('apartment_id', 'cost_type_id', name='uq_apartment_cost_type_share')
        )

    if 'consumption_data' not in existing_tables:
        op.create_table('consumption_data',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('apartment_id', sa.Integer(), nullable=False),
            sa.Column('cost_type_id', sa.Integer(), nullable=False),
            sa.Column('date', sa.DateTime(), nullable=False),
            sa.Column('value', sa.Float(), nullable=False),
            sa.Column('entry_type', sa.String(length=20), server_default='csv_import', nullable=False),
            sa.ForeignKeyConstraint(['apartment_id'], ['apartment.id'], ),
            sa.ForeignKeyConstraint(['cost_type_id'], ['cost_type.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    # Indexe anlegen, falls Tabelle existiert und Index fehlt
    if 'consumption_data' in existing_tables:
        existing_indexes = {idx['name'] for idx in inspector.get_indexes('consumption_data')}
        if 'ix_consumption_data_apartment_cost_type_date' not in existing_indexes:
            op.create_index('ix_consumption_data_apartment_cost_type_date', 'consumption_data', ['apartment_id', 'cost_type_id', 'date'], unique=False)

    if 'contract' not in existing_tables:
        op.create_table('contract',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('tenant_id', sa.Integer(), nullable=False),
            sa.Column('apartment_id', sa.Integer(), nullable=False),
            sa.Column('start_date', sa.Date(), nullable=False),
            sa.Column('end_date', sa.Date(), nullable=True),
            sa.Column('rent_amount', sa.Float(), nullable=False),
            sa.Column('index_clause_base_value', sa.Float(), nullable=True),
            sa.Column('index_clause_base_date', sa.Date(), nullable=True),
            sa.Column('contract_pdf_filename', sa.String(length=255), nullable=True),
            sa.CheckConstraint('end_date IS NULL OR end_date > start_date', name='check_contract_dates'),
            sa.ForeignKeyConstraint(['apartment_id'], ['apartment.id'], ),
            sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    if 'meter' not in existing_tables:
        op.create_table('meter',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('apartment_id', sa.Integer(), nullable=False),
            sa.Column('meter_type', sa.String(length=50), nullable=False),
            sa.Column('serial_number', sa.String(length=100), nullable=False),
            sa.Column('unit', sa.String(length=20), nullable=False),
            sa.ForeignKeyConstraint(['apartment_id'], ['apartment.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('serial_number')
        )
        with op.batch_alter_table('meter', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_meter_apartment_id'), ['apartment_id'], unique=False)

    if 'occupancy_period' not in existing_tables:
        op.create_table('occupancy_period',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('apartment_id', sa.Integer(), nullable=False),
            sa.Column('start_date', sa.Date(), nullable=False),
            sa.Column('end_date', sa.Date(), nullable=True),
            sa.Column('number_of_occupants', sa.Integer(), nullable=False),
            sa.CheckConstraint('end_date IS NULL OR end_date > start_date', name='check_occupancy_period_dates'),
            sa.CheckConstraint('number_of_occupants > 0', name='check_positive_occupants'),
            sa.ForeignKeyConstraint(['apartment_id'], ['apartment.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('occupancy_period', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_occupancy_period_apartment_id'), ['apartment_id'], unique=False)
            batch_op.create_index(batch_op.f('ix_occupancy_period_end_date'), ['end_date'], unique=False)
            batch_op.create_index(batch_op.f('ix_occupancy_period_start_date'), ['start_date'], unique=False)

    if 'invoice' not in existing_tables:
        op.create_table('invoice',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('invoice_number', sa.String(length=100), nullable=True),
            sa.Column('date', sa.Date(), nullable=False),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('cost_type_id', sa.Integer(), nullable=False),
            sa.Column('period_start', sa.Date(), nullable=False),
            sa.Column('period_end', sa.Date(), nullable=False),
            sa.Column('direct_allocation_contract_id', sa.Integer(), nullable=True),
            sa.CheckConstraint('period_end >= period_start', name='check_invoice_period_dates'),
            sa.ForeignKeyConstraint(['cost_type_id'], ['cost_type.id'], ),
            sa.ForeignKeyConstraint(['direct_allocation_contract_id'], ['contract.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('invoice', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_invoice_cost_type_id'), ['cost_type_id'], unique=False)
            batch_op.create_index(batch_op.f('ix_invoice_date'), ['date'], unique=False)
            batch_op.create_index(batch_op.f('ix_invoice_direct_allocation_contract_id'), ['direct_allocation_contract_id'], unique=False)
            batch_op.create_index(batch_op.f('ix_invoice_invoice_number'), ['invoice_number'], unique=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('invoice', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_invoice_invoice_number'))
        batch_op.drop_index(batch_op.f('ix_invoice_direct_allocation_contract_id'))
        batch_op.drop_index(batch_op.f('ix_invoice_date'))
        batch_op.drop_index(batch_op.f('ix_invoice_cost_type_id'))

    op.drop_table('invoice')
    with op.batch_alter_table('occupancy_period', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_occupancy_period_start_date'))
        batch_op.drop_index(batch_op.f('ix_occupancy_period_end_date'))
        batch_op.drop_index(batch_op.f('ix_occupancy_period_apartment_id'))

    op.drop_table('occupancy_period')
    with op.batch_alter_table('meter', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_meter_apartment_id'))

    op.drop_table('meter')
    op.drop_table('contract')
    op.drop_table('consumption_data')
    op.drop_table('apartment_share')
    op.drop_table('tenant')
    op.drop_table('cost_type')
    with op.batch_alter_table('apartment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_apartment_number'))

    op.drop_table('apartment')
    # ### end Alembic commands ###

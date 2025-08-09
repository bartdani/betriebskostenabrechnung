"""Add Building model and link to Apartment/Invoice

Revision ID: aaaa_building_0001
Revises: 5bab8952e54e
Create Date: 2025-08-09 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import Integer, String


revision = 'aaaa_building_0001'
down_revision = '5bab8952e54e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'building',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('address', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
    )

    # Neue Spalten
    with op.batch_alter_table('apartment') as batch_op:
        batch_op.add_column(sa.Column('building_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_apartment_building_id'), ['building_id'], unique=False)
        batch_op.create_foreign_key('fk_apartment_building', 'building', ['building_id'], ['id'])

    with op.batch_alter_table('invoice') as batch_op:
        batch_op.add_column(sa.Column('building_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_invoice_building_id'), ['building_id'], unique=False)
        batch_op.create_foreign_key('fk_invoice_building', 'building', ['building_id'], ['id'])

    # Default-Building einfügen
    conn = op.get_bind()
    conn.execute(sa.text("INSERT INTO building (name, address) VALUES (:n, :a)"), {'n': 'Standardobjekt', 'a': ''})
    res = conn.execute(sa.text("SELECT id FROM building WHERE name=:n"), {'n': 'Standardobjekt'})
    default_id = res.scalar()

    # Bestehende Apartments auf Default setzen
    conn.execute(sa.text("UPDATE apartment SET building_id=:bid WHERE building_id IS NULL"), {'bid': default_id})

    # Invoice.building_id aus Contract->Apartment ableiten, falls möglich
    conn.execute(sa.text(
        """
        UPDATE invoice
        SET building_id = (
            SELECT apartment.building_id
            FROM contract
            JOIN apartment ON apartment.id = contract.apartment_id
            WHERE contract.id = invoice.direct_allocation_contract_id
        )
        WHERE invoice.direct_allocation_contract_id IS NOT NULL
        """
    ))

    # Restliche Rechnungen auf Default setzen, falls immer noch NULL
    conn.execute(sa.text("UPDATE invoice SET building_id=:bid WHERE building_id IS NULL"), {'bid': default_id})

    # Optional: NOT NULL durchsetzen (später)
    # op.alter_column('apartment', 'building_id', nullable=False)
    # op.alter_column('invoice', 'building_id', nullable=False)


def downgrade():
    op.drop_constraint('fk_invoice_building', 'invoice', type_='foreignkey')
    op.drop_index(op.f('ix_invoice_building_id'), table_name='invoice')
    op.drop_column('invoice', 'building_id')

    op.drop_constraint('fk_apartment_building', 'apartment', type_='foreignkey')
    op.drop_index(op.f('ix_apartment_building_id'), table_name='apartment')
    op.drop_column('apartment', 'building_id')

    op.drop_table('building')



import pytest
from app.models import Apartment, Tenant, CostType, ConsumptionData, Contract, Meter, Invoice
from datetime import datetime, date

# Die Fixtures 'app_context' und 'test_db' werden aus conftest.py verwendet.

def test_create_apartment(test_db):
    """Testet das Erstellen und Speichern eines Apartment-Objekts inkl. neuer Felder."""
    a = Apartment(number='Top 1', address='Teststraße 1', size_sqm=75.5)
    test_db.session.add(a)
    test_db.session.commit()
    
    retrieved_a = Apartment.query.filter_by(number='Top 1').first()
    assert retrieved_a is not None
    assert retrieved_a.number == 'Top 1'
    assert retrieved_a.address == 'Teststraße 1'
    assert retrieved_a.size_sqm == 75.5

def test_create_tenant(test_db):
    """Testet das Erstellen und Speichern eines Tenant-Objekts."""
    t = Tenant(name='Max Mustermann', contact_info='max@test.com')
    test_db.session.add(t)
    test_db.session.commit()
    
    retrieved_t = Tenant.query.filter_by(name='Max Mustermann').first()
    assert retrieved_t is not None
    assert retrieved_t.name == 'Max Mustermann'
    assert retrieved_t.contact_info == 'max@test.com'

def test_create_cost_type(test_db):
    """Testet das Erstellen und Speichern eines CostType-Objekts."""
    ct = CostType(name='Heizung', unit='kWh', type='consumption')
    test_db.session.add(ct)
    test_db.session.commit()
    
    retrieved_ct = CostType.query.filter_by(name='Heizung').first()
    assert retrieved_ct is not None
    assert retrieved_ct.unit == 'kWh'
    assert retrieved_ct.type == 'consumption'

def test_create_consumption_data(test_db):
    """Testet das Erstellen und Speichern eines ConsumptionData-Objekts mit Beziehungen."""
    a = Apartment(number='Top 3', address='Musterweg 3', size_sqm=60.0)
    ct = CostType(name='Wasser', unit='m³', type='consumption')
    test_db.session.add_all([a, ct])
    test_db.session.commit()
    
    apt_id = a.id
    ct_id = ct.id
    
    cd = ConsumptionData(
        apartment_id=apt_id, 
        cost_type_id=ct_id, 
        value=123.45,
        date=datetime.now()
    )
    test_db.session.add(cd)
    test_db.session.commit()
    
    saved_cd = ConsumptionData.query.first()
    assert saved_cd is not None
    assert saved_cd.apartment_id == apt_id
    assert saved_cd.cost_type_id == ct_id
    assert saved_cd.value == 123.45
    assert saved_cd.entry_type == 'csv_import'

def test_create_contract(test_db):
    """Testet das Erstellen und Speichern eines Contract-Objekts mit Beziehungen."""
    a = Apartment(number='Top 4', address='Vertragsgasse 4', size_sqm=80.0)
    t = Tenant(name='Vertrags Mieter', contact_info='vertrag@test.com')
    test_db.session.add_all([a, t])
    test_db.session.commit()

    apt_id = a.id
    tenant_id = t.id

    c = Contract(
        tenant_id=tenant_id,
        apartment_id=apt_id,
        start_date=date(2023, 1, 1),
        rent_amount=1000.0,
        index_clause_base_value=150.0,
        index_clause_base_date=date(2022, 12, 1)
    )
    test_db.session.add(c)
    test_db.session.commit()

    retrieved_c = Contract.query.first()
    assert retrieved_c is not None
    assert retrieved_c.tenant_id == tenant_id
    assert retrieved_c.apartment_id == apt_id
    assert retrieved_c.rent_amount == 1000.0
    assert retrieved_c.tenant.name == 'Vertrags Mieter'
    assert retrieved_c.apartment.number == 'Top 4'

def test_create_meter(test_db):
    """Testet das Erstellen und Speichern eines Meter-Objekts."""
    a = Apartment(number='Top 5', address='Zählerweg 5', size_sqm=90.0)
    test_db.session.add(a)
    test_db.session.commit()
    apt_id = a.id

    m = Meter(
        apartment_id=apt_id,
        meter_type='Strom',
        serial_number='XYZ123456',
        unit='kWh'
    )
    test_db.session.add(m)
    test_db.session.commit()

    retrieved_m = Meter.query.filter_by(serial_number='XYZ123456').first()
    assert retrieved_m is not None
    assert retrieved_m.meter_type == 'Strom'
    assert retrieved_m.unit == 'kWh'
    assert retrieved_m.apartment_id == apt_id
    assert retrieved_m.apartment.number == 'Top 5'

def test_create_invoice_direct_allocation(test_db):
    """Testet das Erstellen einer Rechnung mit direkter Vertragszuordnung."""
    a = Apartment(number='Top 6', address='Rechnungstr. 6', size_sqm=100.0)
    t = Tenant(name='Rechnungs Mieter', contact_info='rechnung@test.com')
    ct = CostType(name='Reparatur', unit='EUR', type='share')
    test_db.session.add_all([a, t, ct])
    test_db.session.commit()
    apt_id = a.id
    tenant_id = t.id
    ct_id = ct.id
    c = Contract(tenant_id=tenant_id, apartment_id=apt_id, start_date=date(2023, 1, 1), rent_amount=1200)
    test_db.session.add(c)
    test_db.session.commit()
    contract_id = c.id

    inv = Invoice(
        invoice_number='R123',
        date=date(2024, 1, 15),
        amount=250.75,
        cost_type_id=ct_id,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 10),
        direct_allocation_contract_id=contract_id
    )
    test_db.session.add(inv)
    test_db.session.commit()

    retrieved_inv = Invoice.query.filter_by(invoice_number='R123').first()
    assert retrieved_inv is not None
    assert retrieved_inv.amount == 250.75
    assert retrieved_inv.cost_type_id == ct_id
    assert retrieved_inv.direct_allocation_contract_id == contract_id
    assert retrieved_inv.cost_type.name == 'Reparatur'
    assert retrieved_inv.direct_allocation_contract.tenant.name == 'Rechnungs Mieter'

def test_create_invoice_distributed(test_db):
    """Testet das Erstellen einer Rechnung, die verteilt werden soll (keine direkte Zuordnung)."""
    ct = CostType(name='Allgemeinstrom', unit='kWh', type='consumption')
    test_db.session.add(ct)
    test_db.session.commit()
    ct_id = ct.id

    inv = Invoice(
        invoice_number='R456',
        date=date(2024, 2, 10),
        amount=500.00,
        cost_type_id=ct_id,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        direct_allocation_contract_id=None
    )
    test_db.session.add(inv)
    test_db.session.commit()

    retrieved_inv = Invoice.query.filter_by(invoice_number='R456').first()
    assert retrieved_inv is not None
    assert retrieved_inv.amount == 500.00
    assert retrieved_inv.cost_type_id == ct_id
    assert retrieved_inv.direct_allocation_contract_id is None
    assert retrieved_inv.cost_type.name == 'Allgemeinstrom' 
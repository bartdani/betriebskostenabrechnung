from app import db
from app.models import Apartment, Tenant, Contract, Invoice, CostType
from app.calculations import calculate_direct_allocation
from datetime import date


def setup_contract(apartment_number: str, tenant_name: str, start: date):
    apt = Apartment(number=apartment_number, address=f'{apartment_number} Street', size_sqm=50.0)
    tenant = Tenant(name=tenant_name, contact_info=f'{tenant_name}@example.com')
    db.session.add_all([apt, tenant])
    db.session.commit()
    contract = Contract(tenant_id=tenant.id, apartment_id=apt.id, start_date=start, rent_amount=700.0)
    db.session.add(contract)
    db.session.commit()
    return apt, tenant, contract


def test_direct_allocation_basic(client):
    # Zwei Verträge / Wohnungen
    apt1, _, c1 = setup_contract('A-DIR-1', 'Alice Direct', date(2024, 1, 1))
    apt2, _, c2 = setup_contract('A-DIR-2', 'Bob Direct', date(2024, 1, 1))

    # Kostenart für Vollständigkeit (wird von direct allocation nicht benötigt, aber oft vorhanden)
    ct = CostType(name='Direktkosten-Test', unit='€', type='share')
    db.session.add(ct)
    db.session.commit()

    # Direkte Rechnungen (mit Leistungszeitraum im Abrechnungszeitraum)
    inv1 = Invoice(invoice_number='D-100', date=date(2024, 2, 1), amount=120.0, cost_type_id=ct.id,
                   period_start=date(2024, 1, 1), period_end=date(2024, 1, 31), direct_allocation_contract_id=c1.id)
    inv2 = Invoice(invoice_number='D-101', date=date(2024, 3, 1), amount=80.0, cost_type_id=ct.id,
                   period_start=date(2024, 1, 15), period_end=date(2024, 2, 14), direct_allocation_contract_id=c2.id)
    db.session.add_all([inv1, inv2])
    db.session.commit()

    result = calculate_direct_allocation(period_start=date(2024, 1, 1), period_end=date(2024, 2, 28))

    assert result.get(apt1.id) == 120.0
    assert result.get(apt2.id) == 80.0


def test_direct_allocation_excludes_outside_period(client):
    apt, _, c = setup_contract('A-DIR-3', 'Carol Direct', date(2024, 1, 1))
    ct = CostType(name='Direktkosten-Outside', unit='€', type='share')
    db.session.add(ct)
    db.session.commit()

    # Rechnung komplett außerhalb des Abrechnungszeitraums
    inv = Invoice(invoice_number='D-200', date=date(2023, 12, 15), amount=200.0, cost_type_id=ct.id,
                  period_start=date(2023, 11, 1), period_end=date(2023, 11, 30), direct_allocation_contract_id=c.id)
    db.session.add(inv)
    db.session.commit()

    result = calculate_direct_allocation(period_start=date(2024, 1, 1), period_end=date(2024, 1, 31))
    # Sollte nicht enthalten sein
    assert result.get(apt.id, 0.0) == 0.0



from app import db
from app.models import Apartment, Tenant, Contract, CostType, Invoice
from datetime import date


def setup_invoice_context():
    apt = Apartment(number='APT-INV-1', address='Invoice St 1', size_sqm=60.0)
    tenant = Tenant(name='Invoice Tester', contact_info='inv@test.local')
    db.session.add_all([apt, tenant])
    db.session.commit()
    contract = Contract(tenant_id=tenant.id, apartment_id=apt.id, start_date=date(2024, 1, 1), rent_amount=500.0)
    ct_share = CostType(name='Hausreinigung', unit='€', type='share')
    ct_cons = CostType(name='Kaltwasser', unit='m³', type='consumption')
    db.session.add_all([contract, ct_share, ct_cons])
    db.session.commit()
    return apt, tenant, contract, ct_share, ct_cons


def test_invoices_list_empty(client):
    resp = client.get('/invoices/')
    assert resp.status_code == 200
    assert 'Rechnungsübersicht' in resp.data.decode('utf-8')
    assert 'Keine Rechnungen vorhanden' in resp.data.decode('utf-8')


def test_invoice_create_form_get(client):
    setup_invoice_context()
    resp = client.get('/invoices/new')
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert 'Neue Rechnung' in html
    assert 'name="invoice_number"' in html
    assert 'name="date"' in html
    assert 'name="amount"' in html
    assert 'name="cost_type_id"' in html
    assert 'name="period_start"' in html
    assert 'name="period_end"' in html
    assert 'name="direct_allocation_contract_id"' in html


def test_invoice_create_distributed_success(client):
    _, _, _, ct_share, _ = setup_invoice_context()
    resp = client.post('/invoices/new', data={
        'invoice_number': 'R-1001',
        'date': date(2024, 2, 1),
        'amount': '250.00',
        'cost_type_id': str(ct_share.id),
        'period_start': date(2024, 1, 1),
        'period_end': date(2024, 1, 31),
        'direct_allocation_contract_id': ''
    }, follow_redirects=True)
    assert resp.status_code == 200
    inv = Invoice.query.filter_by(invoice_number='R-1001').first()
    assert inv is not None
    assert inv.direct_allocation_contract_id is None


def test_invoice_create_direct_success(client):
    _, _, contract, _, ct_cons = setup_invoice_context()
    resp = client.post('/invoices/new', data={
        'invoice_number': 'R-1002',
        'date': date(2024, 3, 1),
        'amount': '100.00',
        'cost_type_id': str(ct_cons.id),
        'period_start': date(2024, 2, 1),
        'period_end': date(2024, 2, 28),
        'direct_allocation_contract_id': str(contract.id)
    }, follow_redirects=True)
    assert resp.status_code == 200
    inv = Invoice.query.filter_by(invoice_number='R-1002').first()
    assert inv is not None
    assert inv.direct_allocation_contract_id == contract.id


def test_invoice_create_validation_error(client):
    _, _, _, ct_share, _ = setup_invoice_context()
    # Zeitraum ungültig (Ende vor Start) und fehlender Betrag
    resp = client.post('/invoices/new', data={
        'invoice_number': 'R-ERR',
        'date': date(2024, 1, 10),
        'amount': '',
        'cost_type_id': str(ct_share.id),
        'period_start': date(2024, 2, 1),
        'period_end': date(2024, 1, 31),
        'direct_allocation_contract_id': ''
    })
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert 'Betrag ist erforderlich' in html
    assert 'Ende muss nach Start liegen' in html


def test_invoice_edit_success(client):
    _, _, contract, _, ct_cons = setup_invoice_context()
    inv = Invoice(invoice_number='R-EDIT', date=date(2024, 1, 5), amount=50.0, cost_type_id=ct_cons.id,
                  period_start=date(2024, 1, 1), period_end=date(2024, 1, 31), direct_allocation_contract_id=None)
    db.session.add(inv)
    db.session.commit()
    resp = client.post(f'/invoices/{inv.id}/edit', data={
        'invoice_number': 'R-EDIT-NEW',
        'date': date(2024, 1, 6),
        'amount': '75.0',
        'cost_type_id': str(ct_cons.id),
        'period_start': date(2024, 1, 1),
        'period_end': date(2024, 1, 31),
        'direct_allocation_contract_id': str(contract.id)
    }, follow_redirects=True)
    assert resp.status_code == 200
    updated = db.session.get(Invoice, inv.id)
    assert updated.invoice_number == 'R-EDIT-NEW'
    assert updated.amount == 75.0
    assert updated.direct_allocation_contract_id == contract.id


def test_invoice_edit_not_found(client):
    resp = client.get('/invoices/999/edit')
    assert resp.status_code == 404



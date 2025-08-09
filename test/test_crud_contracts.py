from app import db
from app.models import Apartment, Tenant, Contract
from datetime import date


def setup_contract_context():
    apt = Apartment(number='APT-CTR-1', address='Contract St 1', size_sqm=55.0)
    tenant = Tenant(name='Contract Tester', contact_info='contract@test.local')
    db.session.add_all([apt, tenant])
    db.session.commit()
    return apt, tenant


def test_contracts_list_empty(client):
    resp = client.get('/contracts/')
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert 'Vertragsübersicht' in html
    assert 'Keine Verträge vorhanden' in html


def test_contract_create_form_get(client):
    setup_contract_context()
    resp = client.get('/contracts/new')
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert 'Neuer Vertrag' in html
    assert 'name="tenant_id"' in html
    assert 'name="apartment_id"' in html
    assert 'name="start_date"' in html
    assert 'name="end_date"' in html
    assert 'name="rent_amount"' in html


def test_contract_create_success(client):
    apt, tenant = setup_contract_context()
    resp = client.post('/contracts/new', data={
        'tenant_id': str(tenant.id),
        'apartment_id': str(apt.id),
        'start_date': date(2024, 1, 1),
        'end_date': '',
        'rent_amount': '750.00',
    }, follow_redirects=True)
    assert resp.status_code == 200
    c = Contract.query.first()
    assert c is not None
    assert c.tenant_id == tenant.id
    assert c.apartment_id == apt.id


def test_contract_create_validation_error(client):
    apt, tenant = setup_contract_context()
    # fehlender Betrag und Enddatum < Startdatum
    resp = client.post('/contracts/new', data={
        'tenant_id': str(tenant.id),
        'apartment_id': str(apt.id),
        'start_date': date(2024, 5, 1),
        'end_date': date(2024, 4, 30),
        'rent_amount': '',
    })
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert 'Mietzins ist erforderlich' in html
    assert 'Ende muss nach Start liegen' in html


def test_contract_edit_form(client):
    apt, tenant = setup_contract_context()
    c = Contract(tenant_id=tenant.id, apartment_id=apt.id, start_date=date(2024, 1, 1), rent_amount=700.0)
    db.session.add(c)
    db.session.commit()
    resp = client.get(f'/contracts/{c.id}/edit')
    assert resp.status_code == 200
    assert 'Vertrag bearbeiten' in resp.data.decode('utf-8')


def test_contract_edit_success(client):
    apt, tenant = setup_contract_context()
    c = Contract(tenant_id=tenant.id, apartment_id=apt.id, start_date=date(2024, 1, 1), rent_amount=700.0)
    db.session.add(c)
    db.session.commit()

    resp = client.post(f'/contracts/{c.id}/edit', data={
        'tenant_id': str(tenant.id),
        'apartment_id': str(apt.id),
        'start_date': date(2024, 1, 1),
        'end_date': date(2024, 12, 31),
        'rent_amount': '800.0',
    }, follow_redirects=True)
    assert resp.status_code == 200
    updated = db.session.get(Contract, c.id)
    assert updated.rent_amount == 800.0


def test_contract_edit_not_found(client):
    resp = client.get('/contracts/999/edit')
    assert resp.status_code == 404



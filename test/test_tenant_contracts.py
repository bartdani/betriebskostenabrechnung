import pytest
from datetime import date
from app.models import Apartment, Tenant, Contract
from app import db  # test_db fixture wird aus conftest importiert

# Die Fixtures 'app_context', 'test_db' und 'client' werden aus conftest.py verwendet.

@pytest.fixture
def setup_for_contract_test(test_db):
    """Erstellt notwendige Stammdaten für Contract-Tests."""
    a = Apartment(number='WE 101')
    t = Tenant(name='Test Mieter', apartment=a)
    test_db.session.add_all([a, t])
    test_db.session.commit()
    # IDs zurückgeben, da sie nach commit zugewiesen werden
    return {'tenant_id': t.id, 'apartment_id': a.id, 'db': test_db}

def test_create_contract(setup_for_contract_test):
    """Testet das Erstellen und Speichern eines Contract-Objekts."""
    data = setup_for_contract_test
    test_db = data['db']

    c = Contract(
        tenant_id=data['tenant_id'],
        apartment_id=data['apartment_id'],
        start_date=date(2023, 1, 1),
        rent_amount=500.00,
        index_clause_base_value=110.5,
        index_clause_base_date=date(2022, 12, 1)
    )
    test_db.session.add(c)
    test_db.session.commit()

    retrieved_c = Contract.query.filter_by(rent_amount=500.00).first()
    assert retrieved_c is not None
    assert retrieved_c.tenant_id == data['tenant_id']
    assert retrieved_c.apartment_id == data['apartment_id']
    assert retrieved_c.start_date == date(2023, 1, 1)
    assert retrieved_c.index_clause_base_value == 110.5

def test_contract_route_access(client):
    """Testet, ob die Contract-Übersichtsroute erreichbar ist."""
    # Beachte den Blueprint-Prefix '/tenants'
    response = client.get('/tenants/contracts')
    assert response.status_code == 200
    assert b"Mietvertr\xc3\xa4ge" in response.data # Prüft auf den Titel im Template (UTF-8 encoded) 
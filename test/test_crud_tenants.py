import pytest
from app import db
from app.models import Tenant

def test_list_tenants_empty(client):
    """Test der Listenansicht ohne Mieter"""
    response = client.get('/tenants/')
    assert response.status_code == 200
    assert 'Keine Mieter vorhanden'.encode('utf-8') in response.data

def test_list_tenants_with_data(client):
    """Test der Listenansicht mit einem Mieter"""
    tenant = Tenant(name='Max Mustermann', contact_info='max@example.com')
    db.session.add(tenant)
    db.session.commit()

    response = client.get('/tenants/')
    assert response.status_code == 200
    assert 'Max Mustermann'.encode('utf-8') in response.data
    assert 'max@example.com'.encode('utf-8') in response.data

def test_create_tenant_form(client):
    """Test des Formulars für neue Mieter"""
    response = client.get('/tenants/new')
    assert response.status_code == 200
    assert 'Neuer Mieter'.encode('utf-8') in response.data
    assert 'name="name"'.encode('utf-8') in response.data
    assert 'name="contact_info"'.encode('utf-8') in response.data

def test_create_tenant_success(client):
    """Test der erfolgreichen Mieter-Erstellung"""
    response = client.post('/tenants/new', data={
        'name': 'Erika Musterfrau',
        'contact_info': 'erika@example.com'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Prüfen der Existenz in der Datenbank
    tenant = Tenant.query.filter_by(name='Erika Musterfrau').first()
    assert tenant is not None
    assert tenant.contact_info == 'erika@example.com'
    
    # Prüfen der Flash-Message (weniger strikt)
    assert b'Erika Musterfrau' in response.data
    assert b'erfolgreich erstellt' in response.data
    assert b'alert-success' in response.data

def test_create_tenant_validation_error(client):
    """Test der Validierungsfehler bei der Mieter-Erstellung"""
    # Test: Leerer Name
    response = client.post('/tenants/new', data={
        'name': '',
        'contact_info': 'test@example.com'
    })
    assert response.status_code == 200
    assert 'Name ist erforderlich'.encode('utf-8') in response.data

    # Test: Name zu lang
    response = client.post('/tenants/new', data={
        'name': 'a' * 101,  # 101 Zeichen
        'contact_info': 'test@example.com'
    })
    assert response.status_code == 200
    assert 'Name darf maximal 100 Zeichen lang sein'.encode('utf-8') in response.data

def test_edit_tenant_form(client):
    """Test des Bearbeitungsformulars"""
    # Mieter erstellen
    tenant = Tenant(name='Hans Test', contact_info='hans@example.com')
    db.session.add(tenant)
    db.session.commit()

    response = client.get(f'/tenants/{tenant.id}/edit')
    assert response.status_code == 200
    assert 'Mieter bearbeiten'.encode('utf-8') in response.data
    assert 'Hans Test'.encode('utf-8') in response.data
    assert 'hans@example.com'.encode('utf-8') in response.data

def test_edit_tenant_success(client):
    """Test der erfolgreichen Mieter-Bearbeitung"""
    # Mieter erstellen
    tenant = Tenant(name='Hans Test', contact_info='hans@example.com')
    db.session.add(tenant)
    db.session.commit()

    # Mieter bearbeiten
    response = client.post(f'/tenants/{tenant.id}/edit', data={
        'name': 'Hans Update',
        'contact_info': 'hans.update@example.com'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Prüfen der Datenbankaktualisierung
    updated_tenant = db.session.get(Tenant, tenant.id)
    assert updated_tenant.name == 'Hans Update'
    assert updated_tenant.contact_info == 'hans.update@example.com'
    
    # Prüfen der Flash-Message (weniger strikt)
    assert b'Hans Update' in response.data
    assert b'erfolgreich aktualisiert' in response.data
    assert b'alert-success' in response.data

def test_edit_tenant_validation_error(client):
    """Test der Validierungsfehler bei der Mieter-Bearbeitung"""
    # Mieter erstellen
    tenant = Tenant(name='Hans Test', contact_info='hans@example.com')
    db.session.add(tenant)
    db.session.commit()

    # Test: Leerer Name
    response = client.post(f'/tenants/{tenant.id}/edit', data={
        'name': '',
        'contact_info': 'test@example.com'
    })
    assert response.status_code == 200
    assert 'Name ist erforderlich'.encode('utf-8') in response.data

def test_edit_tenant_not_found(client):
    """Test des 404-Fehlers bei nicht existierendem Mieter"""
    response = client.get('/tenants/999/edit')
    assert response.status_code == 404 
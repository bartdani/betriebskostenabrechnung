import pytest
from app import app, db
from app.models import Apartment

# Fixtures 'client' und 'test_db' werden von conftest.py bereitgestellt

def test_list_apartments_get(client, test_db):
    """Testet das Abrufen der Wohnungsliste via GET."""
    response = client.get('/apartments/')
    assert response.status_code == 200
    assert b"Wohnungs\xc3\xbcbersicht" in response.data

def test_create_apartment_get(client, test_db):
    """Testet das Abrufen des Erstellungsformulars via GET."""
    response = client.get('/apartments/new')
    assert response.status_code == 200
    assert b"Neue Wohnung anlegen" in response.data

def test_edit_apartment_get(client, test_db):
    """Testet das Abrufen des Bearbeitungsformulars via GET."""
    test_db.create_all() # Workaround
    # Erstelle eine Test-Wohnung
    apartment = Apartment(number='TestEdit', address='Edit St', size_sqm=42.0)
    test_db.session.add(apartment)
    test_db.session.commit()
    apt_id = apartment.id

    response = client.get(f'/apartments/{apt_id}/edit')
    assert response.status_code == 200
    assert b"Wohnung bearbeiten" in response.data
    assert b'TestEdit' in response.data
    assert b'Edit St' in response.data
    assert b'42.0' in response.data

def test_edit_apartment_get_not_found(client, test_db):
    """Testet das Abrufen des Bearbeitungsformulars für eine nicht existierende Wohnung."""
    response = client.get('/apartments/999/edit')
    assert response.status_code == 404

def test_create_apartment_post_success(client, test_db):
    """Testet das erfolgreiche Erstellen einer Wohnung via POST."""
    test_db.create_all() # Workaround
    with client:  # Kontext-Manager für Session-Zugriff
        response = client.post('/apartments/new', data={
            'number': 'PostTest',
            'address': 'Post Street 123',
            'size_sqm': '101.5' # Muss als String gesendet werden, wie im HTML-Formular
        }, follow_redirects=True) # Wichtig: Redirect zur Liste folgen

        assert response.status_code == 200 # Nach Redirect ist es die Listenansicht
        assert b'PostTest' in response.data # Prüfen, ob die neue Wohnung in der Liste erscheint

        # Flash-Nachricht im HTML-Response prüfen
        assert b'alert-success' in response.data
        assert b'Wohnung "PostTest" erfolgreich angelegt.' in response.data

def test_edit_apartment_post_success(client, test_db):
    """Testet das erfolgreiche Bearbeiten einer Wohnung via POST."""
    test_db.create_all() # Workaround
    # Erstelle eine Test-Wohnung
    apartment = Apartment(number='TestEditPost', address='Before Edit St', size_sqm=44.0)
    test_db.session.add(apartment)
    test_db.session.commit()
    apt_id = apartment.id

    with client:  # Kontext-Manager für Session-Zugriff
        response = client.post(f'/apartments/{apt_id}/edit', data={
            'number': 'TestEditPostUpdated',
            'address': 'After Edit Street 99',
            'size_sqm': '45.5'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'TestEditPostUpdated' in response.data
        assert b'After Edit Street 99' in response.data

        # Flash-Nachricht im HTML-Response prüfen
        assert b'alert-success' in response.data
        assert b'Wohnung "TestEditPostUpdated" erfolgreich aktualisiert.' in response.data

def test_create_apartment_post_validation_error(client, test_db):
    """Testet die Validierung beim Erstellen einer Wohnung."""
    response = client.post('/apartments/new', data={
        'number': '', # Leer, sollte Fehler geben
        'address': 'Test Address',
        'size_sqm': '50.0'
    })
    assert response.status_code == 200 # Kein Redirect
    assert b"Neue Wohnung anlegen" in response.data
    assert b"Bitte geben Sie eine Wohnungsnummer ein." in response.data

def test_edit_apartment_post_validation_error(client, test_db):
    """Testet die Validierung beim Bearbeiten einer Wohnung."""
    test_db.create_all() # Workaround
    # Erstelle eine Test-Wohnung
    apartment = Apartment(number='TestEditValidation', address='Valid St', size_sqm=60.0)
    test_db.session.add(apartment)
    test_db.session.commit()
    apt_id = apartment.id

    response = client.post(f'/apartments/{apt_id}/edit', data={
        'number': '', # Leer, sollte Fehler geben
        'address': 'New Address',
        'size_sqm': '61.0'
    })
    assert response.status_code == 200 # Kein Redirect
    assert b"Wohnung bearbeiten" in response.data
    assert b"Bitte geben Sie eine Wohnungsnummer ein." in response.data

def test_create_apartment_post_duplicate_number(client, test_db):
    """Testet das Erstellen einer Wohnung mit einer bereits existierenden Nummer."""
    test_db.create_all() # Workaround
    # Erstelle eine existierende Wohnung
    existing_apt = Apartment(number='DuplicateNum', address='Origin St', size_sqm=70.0)
    test_db.session.add(existing_apt)
    test_db.session.commit()

    with client:  # Kontext-Manager für Session-Zugriff
        response = client.post('/apartments/new', data={
            'number': 'DuplicateNum', # Bereits vergeben
            'address': 'New Address',
            'size_sqm': '75.0'
        }, follow_redirects=True)

        assert response.status_code == 200 # Kein Redirect
        assert b"Neue Wohnung anlegen" in response.data

        # Flash-Nachricht im HTML-Response prüfen
        assert b'alert-warning' in response.data
        assert b'Eine Wohnung mit der Nummer "DuplicateNum" existiert bereits.' in response.data

def test_edit_apartment_post_duplicate_number(client, test_db):
    """Testet das Bearbeiten einer Wohnung, wobei die neue Nummer bereits existiert."""
    test_db.create_all() # Workaround
    # Erstelle zwei Wohnungen
    apt1 = Apartment(number='EditNum1', address='Addr 1', size_sqm=80.0)
    apt2 = Apartment(number='EditNum2', address='Addr 2', size_sqm=85.0)
    test_db.session.add_all([apt1, apt2])
    test_db.session.commit()
    apt1_id = apt1.id

    with client:  # Kontext-Manager für Session-Zugriff
        response = client.post(f'/apartments/{apt1_id}/edit', data={
            'number': 'EditNum2', # Nummer von apt2
            'address': 'Addr 1 Updated',
            'size_sqm': '81.0'
        }, follow_redirects=True)

        assert response.status_code == 200 # Kein Redirect
        assert b"Wohnung bearbeiten" in response.data

        # Flash-Nachricht im HTML-Response prüfen
        assert b'alert-warning' in response.data
        assert b'Eine andere Wohnung mit der Nummer "EditNum2" existiert bereits.' in response.data

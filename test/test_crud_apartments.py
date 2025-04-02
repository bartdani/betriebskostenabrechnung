"""
Test suite for apartment CRUD operations.

Best Practices für Flash Message Testing:
----------------------------------------
Siehe systemPatterns.md#flash-message-testing

Wichtige Punkte:
- Keine exakten Nachrichtenvergleiche verwenden
- Prüfung auf Schlüsselwörter statt vollständiger Nachrichten
- HTML-Escaping bei der Überprüfung beachten
- Bootstrap Alert-Klassen in Assertions einbeziehen

Bekannte Workarounds:
--------------------
1. Database Creation:
   ```python
   test_db.create_all()  # Workaround für SQLAlchemy Session-Handling
   ```
   Wird benötigt, um sicherzustellen, dass die Testdatenbank vor jedem Test
   korrekt initialisiert ist.

2. Flash Message Testing:
   ```python
   response_text = response.data.decode('utf-8')
   assert 'alert-success' in response_text  # Prüfe Message-Typ
   assert 'Wohnungsnummer' in response_text  # Prüfe relevanten Inhalt
   ```
"""

import pytest
from app.models import Apartment

# Fixtures 'client' und 'test_db' werden von conftest.py bereitgestellt

def test_list_apartments_get(client):
    """Testet das Abrufen der Wohnungsliste via GET."""
    response = client.get('/apartments/')
    assert response.status_code == 200
    assert b"Wohnungs\xc3\xbcbersicht" in response.data

def test_create_apartment_get(client):
    """Testet das Abrufen des Erstellungsformulars via GET."""
    response = client.get('/apartments/new')
    assert response.status_code == 200
    assert b"Neue Wohnung anlegen" in response.data

def test_edit_apartment_get(client, test_db):
    """Testet das Abrufen des Bearbeitungsformulars via GET."""
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

def test_edit_apartment_get_not_found(client):
    """Testet das Abrufen des Bearbeitungsformulars für eine nicht existierende Wohnung."""
    response = client.get('/apartments/999/edit')
    assert response.status_code == 404

def test_create_apartment_post_success(client):
    """Test successful apartment creation via POST request."""
    response = client.post('/apartments/new',
                          data={'number': '42', 'address': 'Teststraße 1', 'size_sqm': '50.0'},
                          follow_redirects=True)
    
    # Best Practice: Prüfe Nachricht durch mehrere Teil-Assertions
    response_text = response.data.decode('utf-8')
    assert 'alert-success' in response_text  # Message-Typ
    assert '42' in response_text  # Wohnungsnummer
    assert 'erfolgreich' in response_text  # Erfolgsmeldung

    # Verifiziere Datenbank-Eintrag
    apartment = Apartment.query.filter_by(number='42').first()
    assert apartment is not None
    assert apartment.address == 'Teststraße 1'

def test_edit_apartment_post_success(client, test_db):
    """Testet das erfolgreiche Bearbeiten einer Wohnung via POST."""
    test_db.create_all()  # Workaround
    apartment = Apartment(number='TestEditPost', address='Before Edit St', size_sqm=44.0)
    test_db.session.add(apartment)
    test_db.session.commit()
    apt_id = apartment.id

    response = client.post(f'/apartments/{apt_id}/edit', data={
        'number': 'TestEditPostUpdated',
        'address': 'After Edit Street 99',
        'size_sqm': '45.5'
    }, follow_redirects=True)

    response_text = response.data.decode('utf-8')
    assert response.status_code == 200
    assert 'TestEditPostUpdated' in response_text  # Prüfe ob der neue Name angezeigt wird
    assert 'After Edit Street 99' in response_text  # Prüfe ob die neue Adresse angezeigt wird
    assert 'alert-success' in response_text  # Prüfe ob es eine Erfolgs-Nachricht gibt
    assert 'erfolgreich' in response_text  # Prüfe ob "erfolgreich" im Text vorkommt

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
    test_db.create_all()  # Workaround
    existing_apt = Apartment(number='DuplicateNum', address='Origin St', size_sqm=70.0)
    test_db.session.add(existing_apt)
    test_db.session.commit()

    response = client.post('/apartments/new', data={
        'number': 'DuplicateNum',
        'address': 'New Address',
        'size_sqm': '75.0'
    }, follow_redirects=True)

    response_text = response.data.decode('utf-8')
    assert response.status_code == 200
    assert 'Neue Wohnung anlegen' in response_text  # Prüfe ob wir auf dem Formular bleiben
    assert 'alert-warning' in response_text  # Prüfe ob es eine Warnung gibt
    assert 'existiert bereits' in response_text  # Prüfe ob die Warnung angezeigt wird

def test_edit_apartment_post_duplicate_number(client, test_db):
    """Testet das Bearbeiten einer Wohnung, wobei die neue Nummer bereits existiert."""
    test_db.create_all()  # Workaround
    apt1 = Apartment(number='EditNum1', address='Addr 1', size_sqm=80.0)
    apt2 = Apartment(number='EditNum2', address='Addr 2', size_sqm=85.0)
    test_db.session.add_all([apt1, apt2])
    test_db.session.commit()
    apt1_id = apt1.id

    response = client.post(f'/apartments/{apt1_id}/edit', data={
        'number': 'EditNum2',
        'address': 'Addr 1 Updated',
        'size_sqm': '81.0'
    }, follow_redirects=True)

    response_text = response.data.decode('utf-8')
    assert response.status_code == 200
    assert 'Wohnung bearbeiten' in response_text  # Prüfe ob wir auf dem Formular bleiben
    assert 'alert-warning' in response_text  # Prüfe ob es eine Warnung gibt
    assert 'existiert bereits' in response_text  # Prüfe ob die Warnung angezeigt wird

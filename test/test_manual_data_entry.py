import pytest
from app import app, db
from app.models import Apartment, CostType, ConsumptionData
from datetime import date, datetime

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False # CSRF für Tests deaktivieren
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # In-Memory DB für Tests

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            # Testdaten erstellen (optional, aber oft nützlich)
            apt1 = Apartment(number='WE01')
            ct1 = CostType(name='Heizung', unit='kWh', type='consumption')
            ct2 = CostType(name='Wasser', unit='m3', type='consumption')
            ct3 = CostType(name='Grundsteuer', unit='EUR', type='share') # Nicht-Verbrauch
            db.session.add_all([apt1, ct1, ct2, ct3])
            db.session.commit()
            yield testing_client
            db.drop_all()

# --- Tests --- 

def test_get_consumption_entry_page(test_client):
    """Testet, ob die Seite für die manuelle Eingabe geladen wird."""
    response = test_client.get('/manual_entry/consumption')
    assert response.status_code == 200
    assert 'Manuelle Verbrauchserfassung'.encode('utf-8') in response.data
    assert 'Wohnung'.encode('utf-8') in response.data
    assert 'Kostenart (Verbrauch)'.encode('utf-8') in response.data
    assert 'Heizung (kWh)'.encode('utf-8') in response.data # Sollte vorhanden sein
    assert 'Wasser (m3)'.encode('utf-8') in response.data   # Sollte vorhanden sein
    assert 'Grundsteuer (EUR)'.encode('utf-8') not in response.data # Sollte NICHT vorhanden sein

def test_post_valid_consumption_data(test_client):
    """Testet das Absenden gültiger Verbrauchsdaten."""
    apt = Apartment.query.filter_by(number='WE01').first()
    ct = CostType.query.filter_by(name='Wasser').first()
    
    response = test_client.post('/manual_entry/consumption', data={
        'apartment_id': apt.id,
        'cost_type_id': ct.id,
        'date': '2024-08-09',
        'value': 123.45
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert 'Verbrauchsdaten erfolgreich manuell hinzugefügt.'.encode('utf-8') in response.data # Erfolg-Flash
    
    # Überprüfen, ob die Daten in der DB gelandet sind
    entry = ConsumptionData.query.filter_by(apartment_id=apt.id, cost_type_id=ct.id).first()
    assert entry is not None
    assert entry.value == 123.45
    assert entry.date == datetime(2024, 8, 9)
    assert entry.entry_type == 'manual'

def test_post_invalid_data(test_client):
    """Testet das Absenden ungültiger Daten (z.B. fehlender Wert)."""
    apt = Apartment.query.filter_by(number='WE01').first()
    ct = CostType.query.filter_by(name='Heizung').first()
    
    response = test_client.post('/manual_entry/consumption', data={
        'apartment_id': apt.id,
        'cost_type_id': ct.id,
        'date': '2024-08-10',
        'value': '' # Fehlender Wert
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert 'This field is required.'.encode('utf-8') in response.data # Fehlermeldung von WTForms
    assert 'Verbrauchsdaten erfolgreich manuell hinzugefügt.'.encode('utf-8') not in response.data

def test_post_invalid_cost_type(test_client):
    """Testet das Absenden mit einer Kostenart, die nicht vom Typ 'consumption' ist."""
    apt = Apartment.query.filter_by(number='WE01').first()
    ct_share = CostType.query.filter_by(type='share').first() # Grundsteuer
    
    response = test_client.post('/manual_entry/consumption', data={
        'apartment_id': apt.id,
        'cost_type_id': ct_share.id, 
        'date': '2024-08-11',
        'value': 50.0
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Erwartet die Flash-Nachricht aus der Route, nicht die WTForms-Validierung
    assert 'Ungültige Kostenart ausgewählt.' in response.get_data(as_text=True)
    assert 'Verbrauchsdaten erfolgreich manuell hinzugefügt.' not in response.get_data(as_text=True)
    
    # Sicherstellen, dass nichts gespeichert wurde
    entry = ConsumptionData.query.filter_by(apartment_id=apt.id, cost_type_id=ct_share.id).first()
    assert entry is None 
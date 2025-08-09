from datetime import date

from app import db
from app.models import Apartment, CostType


def setup_basic_data():
    apt = Apartment(number='WE-A', address='Testweg 1', size_sqm=45.0)
    ct = CostType(name='Kaltwasser', unit='m³', type='consumption')
    db.session.add_all([apt, ct])
    db.session.commit()
    return apt, ct


def test_get_manual_consumption_form(client, test_db):
    setup_basic_data()
    resp = client.get('/manual_entry/consumption')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert 'Manuelle Verbrauchserfassung' in html


def test_post_manual_consumption_success(client, test_db):
    apt, ct = setup_basic_data()
    resp = client.post('/manual_entry/consumption', data={
        'apartment_id': apt.id,
        'cost_type_id': ct.id,
        'date': date(2024, 1, 15),
        'value': 12.3,
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert 'erfolgreich' in resp.get_data(as_text=True).lower()


def test_post_manual_consumption_validation_error(client, test_db):
    apt, _ = setup_basic_data()
    # Kostenart mit falschem Typ
    ct_share = CostType(name='Fläche', unit='m²', type='share')
    db.session.add(ct_share)
    db.session.commit()

    resp = client.post('/manual_entry/consumption', data={
        'apartment_id': apt.id,
        'cost_type_id': ct_share.id,
        'date': date(2024, 2, 1),
        'value': 1.0,
    })
    assert resp.status_code == 200
    assert 'ungültige kostenart' in resp.get_data(as_text=True).lower()

from app import db
from app.models import Apartment, CostType, ConsumptionData
from datetime import date


def setup_consumption_context():
    apt = Apartment(number='APT-MAN-1', address='Manual St 1', size_sqm=40.0)
    ct = CostType(name='Kaltwasser', unit='m³', type='consumption')
    db.session.add_all([apt, ct])
    db.session.commit()
    return apt, ct


def test_manual_consumption_form_get(client):
    # Kontext anlegen, damit Auswahlfelder nicht leer sind
    setup_consumption_context()
    resp = client.get('/manual_entry/consumption')
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert 'Manuelle Verbrauchserfassung' in html
    assert 'name="apartment_id"' in html
    assert 'name="cost_type_id"' in html
    assert 'name="date"' in html
    assert 'name="value"' in html


def test_manual_consumption_post_success(client):
    apt, ct = setup_consumption_context()
    resp = client.post('/manual_entry/consumption', data={
        'apartment_id': str(apt.id),
        'cost_type_id': str(ct.id),
        'date': date(2024, 1, 10),
        'value': '123.45'
    }, follow_redirects=True)
    assert resp.status_code == 200
    entry = ConsumptionData.query.filter_by(apartment_id=apt.id, cost_type_id=ct.id).first()
    assert entry is not None
    assert entry.entry_type == 'manual'


def test_manual_consumption_post_validation_error(client):
    apt, ct = setup_consumption_context()
    # ungültiger cost_type (share)
    ct_share = CostType(name='Wohnfläche', unit='m²', type='share')
    db.session.add(ct_share)
    db.session.commit()

    resp = client.post('/manual_entry/consumption', data={
        'apartment_id': str(apt.id),
        'cost_type_id': str(ct_share.id),
        'date': date(2024, 1, 10),
        'value': '50.0'
    })
    assert resp.status_code == 200
    text = resp.data.decode('utf-8')
    assert 'Ungültige Kostenart ausgewählt.' in text


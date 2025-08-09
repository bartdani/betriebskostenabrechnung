import pytest
from app import db
from app.models import Apartment, Meter


def create_apartment(number="APT-MTR-1"):
    apt = Apartment(number=number, address="Meterstreet 1", size_sqm=50.0)
    db.session.add(apt)
    db.session.commit()
    return apt


def test_list_meters_empty(client):
    response = client.get('/meters/')
    assert response.status_code == 200
    assert 'Keine Zähler vorhanden'.encode('utf-8') in response.data


def test_list_meters_with_data(client):
    apt = create_apartment("APT-MTR-2")
    m = Meter(apartment_id=apt.id, meter_type='Wasser', serial_number='SN-0001', unit='m³')
    db.session.add(m)
    db.session.commit()

    response = client.get('/meters/')
    assert response.status_code == 200
    assert 'SN-0001'.encode('utf-8') in response.data
    assert 'Wasser'.encode('utf-8') in response.data
    assert 'APT-MTR-2'.encode('utf-8') in response.data


def test_create_meter_form(client):
    response = client.get('/meters/new')
    assert response.status_code == 200
    assert 'Neuer Zähler'.encode('utf-8') in response.data
    # Feldnamen grob prüfen
    assert 'name="meter_type"'.encode('utf-8') in response.data
    assert 'name="serial_number"'.encode('utf-8') in response.data
    assert 'name="unit"'.encode('utf-8') in response.data
    assert 'name="apartment_id"'.encode('utf-8') in response.data


def test_create_meter_success(client):
    apt = create_apartment("APT-MTR-3")
    response = client.post('/meters/new', data={
        'meter_type': 'Strom',
        'serial_number': 'SN-0002',
        'unit': 'kWh',
        'apartment_id': str(apt.id)
    }, follow_redirects=True)

    assert response.status_code == 200
    # DB prüfen
    meter = Meter.query.filter_by(serial_number='SN-0002').first()
    assert meter is not None
    assert meter.meter_type == 'Strom'
    assert meter.unit == 'kWh'

    # Flash-Messages (weniger strikt)
    assert 'alert-success' in response.data.decode('utf-8')
    assert 'erfolgreich' in response.data.decode('utf-8')


def test_create_meter_validation_error(client):
    apt = create_apartment("APT-MTR-4")
    response = client.post('/meters/new', data={
        'meter_type': 'Wasser',
        'serial_number': '',  # fehlt
        'unit': 'm³',
        'apartment_id': str(apt.id)
    })
    assert response.status_code == 200
    assert 'Neuer Zähler'.encode('utf-8') in response.data
    assert 'Seriennummer ist erforderlich'.encode('utf-8') in response.data


def test_edit_meter_form(client):
    apt = create_apartment("APT-MTR-5")
    meter = Meter(apartment_id=apt.id, meter_type='Heizung', serial_number='SN-EDIT-1', unit='kWh')
    db.session.add(meter)
    db.session.commit()

    response = client.get(f'/meters/{meter.id}/edit')
    assert response.status_code == 200
    assert 'Zähler bearbeiten'.encode('utf-8') in response.data
    assert 'SN-EDIT-1'.encode('utf-8') in response.data
    assert 'Heizung'.encode('utf-8') in response.data
    assert 'kWh'.encode('utf-8') in response.data


def test_edit_meter_success(client):
    apt = create_apartment("APT-MTR-6")
    meter = Meter(apartment_id=apt.id, meter_type='Wasser', serial_number='SN-EDIT-2', unit='m³')
    db.session.add(meter)
    db.session.commit()

    response = client.post(f'/meters/{meter.id}/edit', data={
        'meter_type': 'Warmwasser',
        'serial_number': 'SN-EDIT-2-NEW',
        'unit': 'm³',
        'apartment_id': str(apt.id)
    }, follow_redirects=True)

    assert response.status_code == 200
    updated = db.session.get(Meter, meter.id)
    assert updated.meter_type == 'Warmwasser'
    assert updated.serial_number == 'SN-EDIT-2-NEW'
    assert 'alert-success' in response.data.decode('utf-8')
    assert 'erfolgreich' in response.data.decode('utf-8')


def test_edit_meter_not_found(client):
    response = client.get('/meters/999/edit')
    assert response.status_code == 404


def test_create_meter_duplicate_serial(client):
    apt = create_apartment("APT-MTR-7")
    m1 = Meter(apartment_id=apt.id, meter_type='Wasser', serial_number='SN-DUP-1', unit='m³')
    db.session.add(m1)
    db.session.commit()

    response = client.post('/meters/new', data={
        'meter_type': 'Strom',
        'serial_number': 'SN-DUP-1',
        'unit': 'kWh',
        'apartment_id': str(apt.id)
    }, follow_redirects=True)

    text = response.data.decode('utf-8')
    assert response.status_code == 200
    assert 'Neuer Zähler' in text  # bleibt auf Formular
    assert 'alert-warning' in text
    assert 'existiert bereits' in text


def test_edit_meter_duplicate_serial(client):
    apt = create_apartment("APT-MTR-8")
    m1 = Meter(apartment_id=apt.id, meter_type='Wasser', serial_number='SN-DUP-2A', unit='m³')
    m2 = Meter(apartment_id=apt.id, meter_type='Strom', serial_number='SN-DUP-2B', unit='kWh')
    db.session.add_all([m1, m2])
    db.session.commit()

    response = client.post(f'/meters/{m1.id}/edit', data={
        'meter_type': 'Wasser',
        'serial_number': 'SN-DUP-2B',  # kollidiert mit m2
        'unit': 'm³',
        'apartment_id': str(apt.id)
    }, follow_redirects=True)

    text = response.data.decode('utf-8')
    assert response.status_code == 200
    assert 'Zähler bearbeiten' in text
    assert 'alert-warning' in text
    assert 'existiert bereits' in text


def test_create_meter_reading_flow(client, test_db):
    # Setup minimal data
    apt = create_apartment("APT-MTR-READ")
    m = Meter(apartment_id=apt.id, meter_type='Wasser', serial_number='SN-READ', unit='m³')
    db.session.add(m)
    db.session.commit()

    # GET form
    resp = client.get('/meters/readings/new')
    assert resp.status_code == 200

    # POST valid value
    from datetime import date
    resp2 = client.post('/meters/readings/new', data={
        'meter_id': m.id,
        'date': date(2024, 3, 1),
        'value': 5.5,
    }, follow_redirects=True)
    assert resp2.status_code == 200
    assert 'Zählerstand wurde gespeichert' in resp2.get_data(as_text=True)



from app import db
from app.models import Apartment, OccupancyPeriod
from datetime import date


def create_apartment(number="APT-OCC-1"):
    apt = Apartment(number=number, address="Occ Street 1", size_sqm=55.0)
    db.session.add(apt)
    db.session.commit()
    return apt


def test_occupancy_list_empty(client):
    apt = create_apartment()
    response = client.get(f'/apartments/{apt.id}/occupancy/')
    assert response.status_code == 200
    assert 'Belegungszeiträume'.encode('utf-8') in response.data
    assert 'Keine Belegungszeiträume vorhanden'.encode('utf-8') in response.data


def test_occupancy_create_form(client):
    apt = create_apartment("APT-OCC-2")
    response = client.get(f'/apartments/{apt.id}/occupancy/new')
    assert response.status_code == 200
    assert 'Neuer Belegungszeitraum'.encode('utf-8') in response.data
    assert 'name="start_date"'.encode('utf-8') in response.data
    assert 'name="end_date"'.encode('utf-8') in response.data
    assert 'name="number_of_occupants"'.encode('utf-8') in response.data


def test_occupancy_create_success(client):
    apt = create_apartment("APT-OCC-3")
    response = client.post(f'/apartments/{apt.id}/occupancy/new', data={
        'start_date': date(2024, 1, 1),
        'end_date': '',
        'number_of_occupants': '2'
    }, follow_redirects=True)
    assert response.status_code == 200
    # DB prüfen
    period = OccupancyPeriod.query.filter_by(apartment_id=apt.id).first()
    assert period is not None
    assert period.number_of_occupants == 2
    # Erfolgsmeldung grob prüfen
    text = response.data.decode('utf-8')
    assert 'alert-success' in text
    assert 'erfolgreich' in text


def test_occupancy_create_validation_error(client):
    apt = create_apartment("APT-OCC-4")
    # fehlender start_date
    response = client.post(f'/apartments/{apt.id}/occupancy/new', data={
        'start_date': '',
        'end_date': '',
        'number_of_occupants': '0'
    })
    assert response.status_code == 200
    text = response.data.decode('utf-8')
    assert 'Startdatum ist erforderlich' in text
    # HTML-Escaping: '>' wird als '&gt;' gerendert
    assert 'Anzahl der Bewohner muss &gt; 0 sein' in text


def test_occupancy_edit_form(client):
    apt = create_apartment("APT-OCC-5")
    period = OccupancyPeriod(apartment_id=apt.id, start_date=date(2024, 1, 1), end_date=None, number_of_occupants=2)
    db.session.add(period)
    db.session.commit()

    response = client.get(f'/apartments/{apt.id}/occupancy/{period.id}/edit')
    assert response.status_code == 200
    assert 'Belegungszeitraum bearbeiten'.encode('utf-8') in response.data


def test_occupancy_edit_success(client):
    apt = create_apartment("APT-OCC-6")
    period = OccupancyPeriod(apartment_id=apt.id, start_date=date(2024, 1, 1), end_date=None, number_of_occupants=2)
    db.session.add(period)
    db.session.commit()

    response = client.post(f'/apartments/{apt.id}/occupancy/{period.id}/edit', data={
        'start_date': date(2024, 1, 1),
        'end_date': date(2024, 12, 31),
        'number_of_occupants': '3'
    }, follow_redirects=True)
    assert response.status_code == 200
    updated = db.session.get(OccupancyPeriod, period.id)
    assert updated.number_of_occupants == 3
    assert 'alert-success' in response.data.decode('utf-8')


def test_occupancy_edit_not_found(client):
    apt = create_apartment("APT-OCC-7")
    response = client.get(f'/apartments/{apt.id}/occupancy/999/edit')
    assert response.status_code == 404



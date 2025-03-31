import pytest
from datetime import date, timedelta
from app import db
from app.models import Apartment, OccupancyPeriod, CostType
from sqlalchemy.exc import IntegrityError
from app.calculations import calculate_person_days, calculate_person_day_allocation

def test_create_occupancy_period(client, test_db):
    """Testet die erfolgreiche Erstellung einer OccupancyPeriod."""
    apt = Apartment(number='Test Apt 1')
    db.session.add(apt)
    db.session.commit()
    assert apt is not None

    period = OccupancyPeriod(
        apartment_id=apt.id,
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31),
        number_of_occupants=2
    )
    db.session.add(period)
    db.session.commit()

    assert period.id is not None
    assert period.apartment_id == apt.id
    assert period.start_date == date(2023, 1, 1)
    assert period.end_date == date(2023, 12, 31)
    assert period.number_of_occupants == 2

def test_occupancy_period_ongoing(client, test_db):
    """Testet eine Periode ohne Enddatum."""
    apt = Apartment(number='Test Apt Ongoing')
    db.session.add(apt)
    db.session.commit()
    period = OccupancyPeriod(
        apartment_id=apt.id,
        start_date=date(2024, 1, 1),
        number_of_occupants=3
    )
    db.session.add(period)
    db.session.commit()
    assert period.end_date is None

def test_occupancy_period_invalid_dates(client, test_db):
    """Testet, ob ein Enddatum vor dem Startdatum einen Fehler auslöst."""
    apt = Apartment(number='Test Apt Invalid Dates')
    db.session.add(apt)
    db.session.commit()
    with pytest.raises(IntegrityError): # Wegen CheckConstraint
        period = OccupancyPeriod(
            apartment_id=apt.id,
            start_date=date(2023, 12, 31),
            end_date=date(2023, 1, 1),
            number_of_occupants=1
        )
        db.session.add(period)
        db.session.commit()
    db.session.rollback()

def test_occupancy_period_zero_occupants(client, test_db):
    """Testet, ob 0 Bewohner einen Fehler auslösen."""
    apt = Apartment(number='Test Apt Zero Occupants')
    db.session.add(apt)
    db.session.commit()
    with pytest.raises(IntegrityError): # Wegen CheckConstraint
        period = OccupancyPeriod(
            apartment_id=apt.id,
            start_date=date(2023, 1, 1),
            number_of_occupants=0
        )
        db.session.add(period)
        db.session.commit()
    db.session.rollback()

# --- Tests für calculate_person_days --- #

def test_calculate_person_days_single_period_full_overlap(client, test_db):
    """Testet einen Belegungszeitraum, der den Abrechnungszeitraum komplett umfasst."""
    apt = Apartment(number='Test Apt Full Overlap')
    db.session.add(apt)
    db.session.commit()
    db.session.add(OccupancyPeriod(apartment_id=apt.id, start_date=date(2023, 1, 1), end_date=date(2023, 12, 31), number_of_occupants=2))
    db.session.commit()

    billing_start = date(2023, 1, 1)
    billing_end = date(2023, 12, 31)
    days = calculate_person_days(apt.id, billing_start, billing_end)
    assert days == 730

def test_calculate_person_days_single_period_partial_overlap_start(client, test_db):
    """Testet Überlappung am Anfang des Abrechnungszeitraums."""
    apt = Apartment(number='Test Apt Partial Start')
    db.session.add(apt)
    db.session.commit()
    db.session.add(OccupancyPeriod(apartment_id=apt.id, start_date=date(2022, 12, 1), end_date=date(2023, 1, 10), number_of_occupants=1))
    db.session.commit()

    billing_start = date(2023, 1, 1)
    billing_end = date(2023, 12, 31)
    days = calculate_person_days(apt.id, billing_start, billing_end)
    assert days == 10

def test_calculate_person_days_single_period_partial_overlap_end(client, test_db):
    """Testet Überlappung am Ende des Abrechnungszeitraums."""
    apt = Apartment(number='Test Apt Partial End')
    db.session.add(apt)
    db.session.commit()
    db.session.add(OccupancyPeriod(apartment_id=apt.id, start_date=date(2023, 12, 20), end_date=date(2024, 1, 5), number_of_occupants=3))
    db.session.commit()

    billing_start = date(2023, 1, 1)
    billing_end = date(2023, 12, 31)
    days = calculate_person_days(apt.id, billing_start, billing_end)
    assert days == 12 * 3

def test_calculate_person_days_single_period_within(client, test_db):
    """Testet einen Belegungszeitraum komplett innerhalb des Abrechnungszeitraums."""
    apt = Apartment(number='Test Apt Within')
    db.session.add(apt)
    db.session.commit()
    db.session.add(OccupancyPeriod(apartment_id=apt.id, start_date=date(2023, 2, 1), end_date=date(2023, 2, 10), number_of_occupants=4))
    db.session.commit()

    billing_start = date(2023, 1, 1)
    billing_end = date(2023, 12, 31)
    days = calculate_person_days(apt.id, billing_start, billing_end)
    assert days == 40

def test_calculate_person_days_multiple_periods(client, test_db):
    """Testet mehrere Belegungszeiträume."""
    apt = Apartment(number='Test Apt Multi')
    db.session.add(apt)
    db.session.commit()
    db.session.add_all([
        OccupancyPeriod(apartment_id=apt.id, start_date=date(2023, 1, 1), end_date=date(2023, 1, 10), number_of_occupants=2), # 10 Tage * 2 = 20
        OccupancyPeriod(apartment_id=apt.id, start_date=date(2023, 1, 11), end_date=date(2023, 1, 20), number_of_occupants=3)  # 10 Tage * 3 = 30
    ])
    db.session.commit()

    billing_start = date(2023, 1, 1)
    billing_end = date(2023, 12, 31)
    days = calculate_person_days(apt.id, billing_start, billing_end)
    assert days == 20 + 30

def test_calculate_person_days_ongoing_period(client, test_db):
    """Testet eine laufende Belegungsperiode."""
    apt = Apartment(number='Test Apt Ongoing Calc')
    db.session.add(apt)
    db.session.commit()
    db.session.add(OccupancyPeriod(apartment_id=apt.id, start_date=date(2023, 12, 1), number_of_occupants=1))
    db.session.commit()

    billing_start = date(2023, 1, 1)
    billing_end = date(2023, 12, 31)
    days = calculate_person_days(apt.id, billing_start, billing_end)
    assert days == 31

def test_calculate_person_days_no_overlap(client, test_db):
    """Testet einen Belegungszeitraum außerhalb des Abrechnungszeitraums."""
    apt = Apartment(number='Test Apt No Overlap')
    db.session.add(apt)
    db.session.commit()
    db.session.add(OccupancyPeriod(apartment_id=apt.id, start_date=date(2022, 1, 1), end_date=date(2022, 12, 31), number_of_occupants=2))
    db.session.commit()

    billing_start = date(2023, 1, 1)
    billing_end = date(2023, 12, 31)
    days = calculate_person_days(apt.id, billing_start, billing_end)
    assert days == 0

def test_calculate_person_days_no_periods(client, test_db):
    """Testet den Fall ohne Belegungszeiträume für die Wohnung."""
    apt = Apartment(number='Test Apt No Periods')
    db.session.add(apt)
    db.session.commit()
    billing_start = date(2023, 1, 1)
    billing_end = date(2023, 12, 31)
    days = calculate_person_days(apt.id, billing_start, billing_end)
    assert days == 0

# --- Tests für calculate_person_day_allocation --- #

def test_calculate_person_day_allocation_simple(client, test_db):
    """Testet eine einfache Verteilung auf zwei Wohnungen."""
    apt1 = Apartment(number='Alloc Apt 1')
    apt2 = Apartment(number='Alloc Apt 2')
    db.session.add_all([apt1, apt2])
    db.session.commit()

    db.session.add(OccupancyPeriod(apartment_id=apt1.id, start_date=date(2023, 1, 1), end_date=date(2023, 1, 10), number_of_occupants=2))
    db.session.add(OccupancyPeriod(apartment_id=apt2.id, start_date=date(2023, 1, 1), end_date=date(2023, 1, 10), number_of_occupants=3))
    db.session.commit()

    billing_start = date(2023, 1, 1)
    billing_end = date(2023, 12, 31)
    total_cost = 100.0

    allocation = calculate_person_day_allocation(999, total_cost, billing_start, billing_end)

    assert len(allocation) == 2
    assert allocation[apt1.id] == 40.00
    assert allocation[apt2.id] == 60.00

def test_calculate_person_day_allocation_one_apartment_zero_days(client, test_db):
    """Testet Verteilung, wenn eine Wohnung keine Personentage hat."""
    apt1 = Apartment(number='Alloc Zero 1')
    apt2 = Apartment(number='Alloc Zero 2')
    db.session.add_all([apt1, apt2])
    db.session.commit()

    db.session.add(OccupancyPeriod(apartment_id=apt1.id, start_date=date(2023, 1, 1), end_date=date(2023, 1, 10), number_of_occupants=2))
    db.session.commit()

    billing_start = date(2023, 1, 1)
    billing_end = date(2023, 12, 31)
    total_cost = 100.0

    allocation = calculate_person_day_allocation(999, total_cost, billing_start, billing_end)

    assert len(allocation) == 2
    assert allocation[apt1.id] == 100.00
    assert allocation[apt2.id] == 0.00

def test_calculate_person_day_allocation_total_zero_days(client, test_db):
    """Testet Verteilung, wenn insgesamt keine Personentage anfallen."""
    apt1 = Apartment(number='Alloc Total Zero 1')
    apt2 = Apartment(number='Alloc Total Zero 2')
    db.session.add_all([apt1, apt2])
    db.session.commit()

    db.session.commit()

    billing_start = date(2023, 1, 1)
    billing_end = date(2023, 12, 31)
    total_cost = 100.0

    allocation = calculate_person_day_allocation(999, total_cost, billing_start, billing_end)

    assert len(allocation) == 2
    assert allocation[apt1.id] == 0.00
    assert allocation[apt2.id] == 0.00 
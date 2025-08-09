from datetime import date, datetime
from app import db
from app.models import Apartment, CostType, ConsumptionData
from app.validation import generate_warnings


def setup_basic_consumption():
    a1 = Apartment(number='W-1', address='Warnstr 1', size_sqm=45.0)
    a2 = Apartment(number='W-2', address='Warnstr 2', size_sqm=55.0)
    db.session.add_all([a1, a2])
    db.session.commit()

    ct = CostType(name='Kaltwasser-Warn', unit='m³', type='consumption')
    db.session.add(ct)
    db.session.commit()

    return a1, a2, ct


def test_missing_consumption_warning_for_apartment(client):
    a1, a2, ct = setup_basic_consumption()
    # Nur für a1 Verbrauch erfassen, a2 fehlt im Zeitraum
    db.session.add(
        ConsumptionData(apartment_id=a1.id, cost_type_id=ct.id, date=datetime(2024, 1, 10), value=12.0)
    )
    db.session.commit()

    warnings = generate_warnings(period_start=date(2024, 1, 1), period_end=date(2024, 1, 31))

    # Erwartung: missing_consumption enthält den fehlenden Apartment-Eintrag
    missing = warnings.get('missing_consumption', [])
    assert any(w['apartment_id'] == a2.id and w['cost_type_id'] == ct.id for w in missing)


def test_invalid_consumption_values_warning(client):
    a1, a2, ct = setup_basic_consumption()
    # Negativer Wert ist ungültig
    db.session.add(
        ConsumptionData(apartment_id=a1.id, cost_type_id=ct.id, date=datetime(2024, 1, 5), value=-3.0)
    )
    db.session.commit()

    warnings = generate_warnings(period_start=date(2024, 1, 1), period_end=date(2024, 1, 31))

    invalids = warnings.get('invalid_consumption_values', [])
    assert any(w['apartment_id'] == a1.id and w['cost_type_id'] == ct.id for w in invalids)


def test_consumption_spikes_warning(client):
    a1, a2, ct = setup_basic_consumption()
    # Normale Werte ~1, ein Ausreißer 10 (> 3 * median(1,1,1) = 3)
    db.session.add_all([
        ConsumptionData(apartment_id=a1.id, cost_type_id=ct.id, date=datetime(2024, 1, 1), value=1.0),
        ConsumptionData(apartment_id=a1.id, cost_type_id=ct.id, date=datetime(2024, 1, 2), value=1.0),
        ConsumptionData(apartment_id=a2.id, cost_type_id=ct.id, date=datetime(2024, 1, 3), value=1.0),
        ConsumptionData(apartment_id=a2.id, cost_type_id=ct.id, date=datetime(2024, 1, 4), value=10.0),
    ])
    db.session.commit()

    warnings = generate_warnings(period_start=date(2024, 1, 1), period_end=date(2024, 1, 31))
    spikes = warnings.get('consumption_spikes', [])
    assert any(w['apartment_id'] == a2.id and w['cost_type_id'] == ct.id and w['value'] == 10.0 for w in spikes)



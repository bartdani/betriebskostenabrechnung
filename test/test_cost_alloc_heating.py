from app import db
from app.models import Apartment, CostType, ConsumptionData
from app.calculations import calculate_heating_allocation
from datetime import date, datetime


def setup_heating_context():
    # Apartments
    a1 = Apartment(number='H-1', address='Heat 1', size_sqm=50.0)
    a2 = Apartment(number='H-2', address='Heat 2', size_sqm=100.0)
    db.session.add_all([a1, a2])
    db.session.commit()

    # CostTypes (beide Verbrauch)
    ct_heat = CostType(name='Heizenergie', unit='kWh', type='consumption')
    ct_hot = CostType(name='Warmwasser', unit='m³', type='consumption')
    db.session.add_all([ct_heat, ct_hot])
    db.session.commit()

    # Verbrauchsdaten im Zeitraum Jan 2024
    # Warmwasser: a1=10, a2=30
    db.session.add_all([
        ConsumptionData(apartment_id=a1.id, cost_type_id=ct_hot.id, date=datetime(2024, 1, 10), value=10.0),
        ConsumptionData(apartment_id=a2.id, cost_type_id=ct_hot.id, date=datetime(2024, 1, 20), value=30.0),
    ])
    # Heizung: a1=100, a2=200
    db.session.add_all([
        ConsumptionData(apartment_id=a1.id, cost_type_id=ct_heat.id, date=datetime(2024, 1, 15), value=100.0),
        ConsumptionData(apartment_id=a2.id, cost_type_id=ct_heat.id, date=datetime(2024, 1, 18), value=200.0),
    ])
    db.session.commit()

    return a1, a2, ct_heat, ct_hot


def test_heating_allocation_basic_split(client):
    a1, a2, ct_heat, ct_hot = setup_heating_context()

    total_cost = 1000.0
    hot_water_percent = 30.0  # 30% Warmwasser, 70% Heizung
    result = calculate_heating_allocation(
        total_cost=total_cost,
        hot_water_percentage=hot_water_percent,
        heating_consumption_cost_type_id=ct_heat.id,
        hot_water_consumption_cost_type_id=ct_hot.id,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
    )

    # Erwartung:
    # Warmwasser 30% von 1000 = 300, verteilt nach 10:30 => 75 / 225
    # Heizung 70% von 1000 = 700, verteilt nach 100:200 => 233.33 / 466.67
    # Summe:
    # a1: 75 + 233.33 = 308.33, a2: 225 + 466.67 = 691.67
    assert round(result[a1.id], 2) == 308.33
    assert round(result[a2.id], 2) == 691.67
    assert round(sum(result.values()), 2) == 1000.0


def test_heating_allocation_no_hot_water_data(client):
    # Keine Warmwasser-Daten, nur Heizung vorhanden
    a1 = Apartment(number='H-3', address='Heat 3', size_sqm=80.0)
    a2 = Apartment(number='H-4', address='Heat 4', size_sqm=120.0)
    db.session.add_all([a1, a2])
    db.session.commit()

    ct_heat = CostType(name='Heizenergie-2', unit='kWh', type='consumption')
    ct_hot = CostType(name='Warmwasser-2', unit='m³', type='consumption')
    db.session.add_all([ct_heat, ct_hot])
    db.session.commit()

    # Nur Heizung: a1=80, a2=120
    db.session.add_all([
        ConsumptionData(apartment_id=a1.id, cost_type_id=ct_heat.id, date=datetime(2024, 2, 10), value=80.0),
        ConsumptionData(apartment_id=a2.id, cost_type_id=ct_heat.id, date=datetime(2024, 2, 12), value=120.0),
    ])
    db.session.commit()

    total_cost = 600.0
    res = calculate_heating_allocation(
        total_cost=total_cost,
        hot_water_percentage=40.0,
        heating_consumption_cost_type_id=ct_heat.id,
        hot_water_consumption_cost_type_id=ct_hot.id,
        period_start=date(2024, 2, 1),
        period_end=date(2024, 2, 28),
    )

    # Warmwasser: keine Daten -> 0 verteilt; Heizung: 60% von 600 = 360 nach 80:120 => 144 / 216
    assert round(res[a1.id], 2) == 144.0
    assert round(res[a2.id], 2) == 216.0
    assert round(sum(res.values()), 2) == 360.0


import pytest
from datetime import date, datetime
from app.models import Apartment, CostType, ConsumptionData
from app.calculations import calculate_consumption_allocation

# Die Fixture 'test_db' wird aus conftest.py verwendet.

@pytest.fixture
def setup_db_for_allocation(test_db):
    """Erstellt notwendige Stammdaten für Verteilungs-Tests."""
    a1 = Apartment(number='Alloc Apt 1')
    a2 = Apartment(number='Alloc Apt 2')
    a3 = Apartment(number='Alloc Apt 3') # Hat keinen Verbrauch im Testzeitraum
    ct_c = CostType(name='VerbrauchKosten', unit='units', type='consumption')
    ct_s = CostType(name='AnteilKosten', unit='m2', type='share') # Für Negativtest
    
    # Verbrauchsdaten für ct_c
    cd1 = ConsumptionData(apartment=a1, cost_type=ct_c, date=date(2023, 5, 10), value=100)
    cd2 = ConsumptionData(apartment=a2, cost_type=ct_c, date=date(2023, 5, 15), value=300)
    cd3 = ConsumptionData(apartment=a1, cost_type=ct_c, date=date(2023, 6, 1), value=50) # Außerhalb Zeitraum für Test 1
    cd4 = ConsumptionData(apartment=a2, cost_type=ct_c, date=date(2023, 4, 30), value=10) # Außerhalb Zeitraum für Test 1
    cd5 = ConsumptionData(apartment=a1, cost_type=ct_c, date=date(2023, 5, 20), value=0) # Null-Verbrauch

    test_db.session.add_all([a1, a2, a3, ct_c, ct_s, cd1, cd2, cd3, cd4, cd5])
    test_db.session.commit()
    
    # IDs zurückgeben
    return {
        'a1_id': a1.id, 
        'a2_id': a2.id, 
        'a3_id': a3.id, 
        'ct_c_id': ct_c.id, 
        'ct_s_id': ct_s.id,
        'db': test_db
    }

def test_consumption_allocation_normal(setup_db_for_allocation):
    """Testet die normale Verteilung basierend auf Verbrauch."""
    data = setup_db_for_allocation
    period_start = date(2023, 5, 1)
    period_end = date(2023, 5, 31)
    total_cost = 800.00
    
    # Erwarteter Verbrauch im Zeitraum: Apt1=100+0=100, Apt2=300. Total=400
    # Erwartete Anteile: Apt1=100/400=0.25 -> 200.00, Apt2=300/400=0.75 -> 600.00
    
    allocation = calculate_consumption_allocation(data['ct_c_id'], total_cost, period_start, period_end)
    
    assert allocation is not None
    assert len(allocation) == 2 # Nur Apartments mit Verbrauch im Zeitraum
    assert data['a1_id'] in allocation
    assert data['a2_id'] in allocation
    assert data['a3_id'] not in allocation # Hatte keinen Verbrauch
    assert allocation[data['a1_id']] == pytest.approx(200.00)
    assert allocation[data['a2_id']] == pytest.approx(600.00)

def test_consumption_allocation_zero_total(setup_db_for_allocation):
    """Testet den Fall, dass der Gesamtverbrauch im Zeitraum 0 ist."""
    data = setup_db_for_allocation
    # Zeitraum wählen, in dem keine Verbräuche stattfinden
    period_start = date(2024, 1, 1)
    period_end = date(2024, 1, 31)
    total_cost = 100.00
    
    allocation = calculate_consumption_allocation(data['ct_c_id'], total_cost, period_start, period_end)
    
    # Funktion gibt leeres Dict zurück, wenn Gesamtverbrauch 0 ist
    assert allocation is not None
    assert len(allocation) == 0 

def test_consumption_allocation_one_apt_zero(setup_db_for_allocation):
    """Testet den Fall, dass ein Apartment 0 Verbrauch hat, andere aber nicht."""
    data = setup_db_for_allocation
    period_start = date(2023, 5, 1)
    period_end = date(2023, 5, 31)
    total_cost = 800.00
    
    # Gleiches Szenario wie normal, Apt1 hat einen Eintrag mit 0.0
    allocation = calculate_consumption_allocation(data['ct_c_id'], total_cost, period_start, period_end)

    assert allocation is not None
    assert len(allocation) == 2 # Apt1 hat 0 Verbrauch, wird aber mit 0.00 gelistet
    assert data['a1_id'] in allocation
    assert data['a2_id'] in allocation
    assert allocation[data['a1_id']] == pytest.approx(200.00) # Berechnung sollte 0 Verbrauch ignorieren
    assert allocation[data['a2_id']] == pytest.approx(600.00)

def test_consumption_allocation_wrong_cost_type(setup_db_for_allocation):
    """Testet, ob None zurückgegeben wird, wenn der CostType nicht 'consumption' ist."""
    data = setup_db_for_allocation
    period_start = date(2023, 5, 1)
    period_end = date(2023, 5, 31)
    total_cost = 100.00
    
    allocation = calculate_consumption_allocation(data['ct_s_id'], total_cost, period_start, period_end)
    
    assert allocation == {}

def test_consumption_allocation_cost_type_not_found(setup_db_for_allocation):
    """Testet, ob None zurückgegeben wird, wenn die CostType ID nicht existiert."""
    data = setup_db_for_allocation
    period_start = date(2023, 5, 1)
    period_end = date(2023, 5, 31)
    total_cost = 100.00
    
    allocation = calculate_consumption_allocation(9999, total_cost, period_start, period_end)
    
    assert allocation == {} 
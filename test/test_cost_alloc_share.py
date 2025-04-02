import pytest
from app.models import Apartment, CostType, ApartmentShare
from app.calculations import calculate_share_allocation

# Die Fixture 'test_db' wird aus conftest.py verwendet.

@pytest.fixture
def setup_db_for_share_allocation(test_db):
    """Erstellt notwendige Stammdaten für Anteil-Verteilungs-Tests."""
    a1 = Apartment(number='Share Apt 1', address='Share St 1', size_sqm=100.0)
    a2 = Apartment(number='Share Apt 2', address='Share St 2', size_sqm=150.0)
    a3 = Apartment(number='Share Apt 3', address='Share St 3', size_sqm=200.0) # Hat keinen Anteilswert für ct_s1
    ct_s1 = CostType(name='Wohnfläche', unit='m²', type='share')
    ct_s2 = CostType(name='Personen', unit='P', type='share')
    ct_c = CostType(name='Heizung ShareTest', unit='kWh', type='consumption') # Für Negativtest
    
    # Anteilswerte für ct_s1 (Wohnfläche)
    ash1 = ApartmentShare(apartment=a1, cost_type=ct_s1, value=50.0)
    ash2 = ApartmentShare(apartment=a2, cost_type=ct_s1, value=150.0)
    # ash3 für a3 wird nicht erstellt
    
    # Anteilswerte für ct_s2 (Personen)
    ash4 = ApartmentShare(apartment=a1, cost_type=ct_s2, value=1.0)
    ash5 = ApartmentShare(apartment=a2, cost_type=ct_s2, value=0.0) # Null Anteil
    ash6 = ApartmentShare(apartment=a3, cost_type=ct_s2, value=2.0)

    test_db.session.add_all([a1, a2, a3, ct_s1, ct_s2, ct_c, ash1, ash2, ash4, ash5, ash6])
    test_db.session.commit()
    
    # IDs zurückgeben
    return {
        'a1_id': a1.id, 
        'a2_id': a2.id, 
        'a3_id': a3.id, 
        'ct_s1_id': ct_s1.id, 
        'ct_s2_id': ct_s2.id, 
        'ct_c_id': ct_c.id,
        'db': test_db
    }

def test_share_allocation_normal(setup_db_for_share_allocation):
    """Testet die normale Verteilung basierend auf Anteilen (Wohnfläche)."""
    data = setup_db_for_share_allocation
    total_cost = 1000.00
    
    # Erwartete Anteile für ct_s1: Apt1=50, Apt2=150. Total=200
    # Erwartete Kosten: Apt1=50/200*1000=250.00, Apt2=150/200*1000=750.00
    
    allocation = calculate_share_allocation(data['ct_s1_id'], total_cost)
    
    assert allocation is not None
    assert len(allocation) == 2 # Nur Apartments mit Anteilswert für diesen CostType
    assert data['a1_id'] in allocation
    assert data['a2_id'] in allocation
    assert data['a3_id'] not in allocation
    assert allocation[data['a1_id']] == pytest.approx(250.00)
    assert allocation[data['a2_id']] == pytest.approx(750.00)

def test_share_allocation_one_share_zero(setup_db_for_share_allocation):
    """Testet die Verteilung, wenn ein Anteil 0 ist (Personen)."""
    data = setup_db_for_share_allocation
    total_cost = 300.00

    # Erwartete Anteile für ct_s2: Apt1=1, Apt2=0, Apt3=2. Total=3
    # Erwartete Kosten: Apt1=1/3*300=100.00, Apt2=0/3*300=0.00, Apt3=2/3*300=200.00
    
    allocation = calculate_share_allocation(data['ct_s2_id'], total_cost)

    assert allocation is not None
    assert len(allocation) == 3 # Alle 3 Apartments haben einen Share-Eintrag für ct_s2
    assert data['a1_id'] in allocation
    assert data['a2_id'] in allocation
    assert data['a3_id'] in allocation
    assert allocation[data['a1_id']] == pytest.approx(100.00)
    assert allocation[data['a2_id']] == pytest.approx(0.00) # Anteil war 0
    assert allocation[data['a3_id']] == pytest.approx(200.00)

def test_share_allocation_zero_total(setup_db_for_share_allocation):
    """Testet den Fall, dass die Summe aller Anteile 0 ist."""
    data = setup_db_for_share_allocation
    test_db = data['db']
    
    # Neuen CostType und Shares mit Wert 0 erstellen
    ct_zero = CostType(name='ZeroShare', unit='N/A', type='share')
    ash_z1 = ApartmentShare(apartment_id=data['a1_id'], cost_type=ct_zero, value=0.0)
    ash_z2 = ApartmentShare(apartment_id=data['a2_id'], cost_type=ct_zero, value=0.0)
    test_db.session.add_all([ct_zero, ash_z1, ash_z2])
    test_db.session.commit()
    
    total_cost = 100.00
    allocation = calculate_share_allocation(ct_zero.id, total_cost)
    
    assert allocation is not None
    assert len(allocation) == 2 # Beide Apartments haben Einträge
    assert allocation[data['a1_id']] == pytest.approx(0.00)
    assert allocation[data['a2_id']] == pytest.approx(0.00)

def test_share_allocation_invalid_cost_type(setup_db_for_share_allocation):
    """Testet die Verteilung mit einer ungültigen CostType ID."""
    data = setup_db_for_share_allocation
    allocation = calculate_share_allocation(9999, 100.0)
    assert allocation == {}

def test_share_allocation_wrong_cost_type(setup_db_for_share_allocation):
    """Testet die Verteilung mit einem CostType vom Typ 'consumption'."""
    data = setup_db_for_share_allocation
    # Finde den consumption CostType aus der Fixture
    consum_ct_id = data['ct_c_id'] 
    allocation = calculate_share_allocation(consum_ct_id, 100.0)
    assert allocation == {}

def test_share_allocation_cost_type_not_found(setup_db_for_share_allocation):
    """Testet, ob ein leeres Dict zurückgegeben wird, wenn die CostType ID nicht existiert."""
    data = setup_db_for_share_allocation
    total_cost = 100.00

    allocation = calculate_share_allocation(9999, total_cost)
    
    assert allocation == {} 
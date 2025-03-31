import pytest
from datetime import date
from app.models import Apartment, CostType, ConsumptionData, ApartmentShare
from app.calculations import calculate_combined_allocation

# Die Fixture 'test_db' wird aus conftest.py verwendet.

@pytest.fixture
def setup_db_for_combined(test_db):
    """Erstellt notwendige Stammdaten für kombinierte Verteilungs-Tests."""
    # Apartments
    a1 = Apartment(number='Comb Apt 1')
    a2 = Apartment(number='Comb Apt 2')
    a3 = Apartment(number='Comb Apt 3') # Nur Anteil, kein Verbrauch

    # CostTypes
    ct_consum = CostType(name='Heizung Kombi', unit='kWh', type='consumption')
    ct_share = CostType(name='Fläche Kombi', unit='m²', type='share')
    
    test_db.session.add_all([a1, a2, a3, ct_consum, ct_share])
    test_db.session.commit() # Commit um IDs zu erhalten
    
    # ConsumptionData (für ct_consum)
    cd1 = ConsumptionData(apartment_id=a1.id, cost_type_id=ct_consum.id, date=date(2023, 7, 10), value=100)
    cd2 = ConsumptionData(apartment_id=a2.id, cost_type_id=ct_consum.id, date=date(2023, 7, 15), value=150)
    # a3 hat keinen Verbrauch
    
    # ApartmentShares (für ct_share)
    ash1 = ApartmentShare(apartment_id=a1.id, cost_type_id=ct_share.id, value=40.0) # 40 m²
    ash2 = ApartmentShare(apartment_id=a2.id, cost_type_id=ct_share.id, value=60.0) # 60 m²
    ash3 = ApartmentShare(apartment_id=a3.id, cost_type_id=ct_share.id, value=100.0) # 100 m²

    test_db.session.add_all([cd1, cd2, ash1, ash2, ash3])
    test_db.session.commit()
    
    # IDs zurückgeben
    return {
        'a1_id': a1.id, 
        'a2_id': a2.id, 
        'a3_id': a3.id, 
        'ct_consum_id': ct_consum.id, 
        'ct_share_id': ct_share.id,
        'db': test_db
    }

def test_combined_allocation_50_50(setup_db_for_combined):
    """Testet eine 50/50 Kombination aus Verbrauch und Anteil."""
    data = setup_db_for_combined
    total_cost_to_allocate = 1000.00
    period_start = date(2023, 7, 1)
    period_end = date(2023, 7, 31)

    rules = [
        {
            'cost_type_id': data['ct_consum_id'],
            'percentage': 50.0,
            'total_cost_part': total_cost_to_allocate * 0.50, # 500.00
            'period_start': period_start,
            'period_end': period_end
        },
        {
            'cost_type_id': data['ct_share_id'],
            'percentage': 50.0,
            'total_cost_part': total_cost_to_allocate * 0.50 # 500.00
            # kein Periodendatum für 'share' nötig
        }
    ]

    # Manuelle Berechnung:
    # Verbrauchsteil (500 €): Apt1=100, Apt2=150. Total=250.
    #   Apt1: (100/250)*500 = 200.00
    #   Apt2: (150/250)*500 = 300.00
    #   Apt3: 0.00
    # Anteilsteil (500 €): Apt1=40, Apt2=60, Apt3=100. Total=200.
    #   Apt1: (40/200)*500 = 100.00
    #   Apt2: (60/200)*500 = 150.00
    #   Apt3: (100/200)*500 = 250.00
    # Gesamt:
    #   Apt1: 200 + 100 = 300.00
    #   Apt2: 300 + 150 = 450.00
    #   Apt3: 0 + 250 = 250.00

    allocation = calculate_combined_allocation(rules)

    assert allocation is not None
    assert len(allocation) == 3 # Alle 3 Apartments sind beteiligt
    assert allocation[data['a1_id']] == pytest.approx(300.00)
    assert allocation[data['a2_id']] == pytest.approx(450.00)
    assert allocation[data['a3_id']] == pytest.approx(250.00)

def test_combined_allocation_only_consumption(setup_db_for_combined):
    """Testet, wenn nur eine Verbrauchsregel übergeben wird."""
    data = setup_db_for_combined
    total_cost_to_allocate = 1000.00
    period_start = date(2023, 7, 1)
    period_end = date(2023, 7, 31)

    rules = [
        {
            'cost_type_id': data['ct_consum_id'],
            'percentage': 100.0, # Achtung: Funktion gibt Warnung aus!
            'total_cost_part': total_cost_to_allocate,
            'period_start': period_start,
            'period_end': period_end
        }
    ]
    # Erwartet: Apt1=(100/250)*1000=400, Apt2=(150/250)*1000=600
    allocation = calculate_combined_allocation(rules)
    assert allocation is not None
    assert len(allocation) == 2
    assert allocation[data['a1_id']] == pytest.approx(400.00)
    assert allocation[data['a2_id']] == pytest.approx(600.00)

def test_combined_allocation_wrong_percentage_sum(setup_db_for_combined):
    """Testet, wenn die Summe der Prozente nicht 100 ist (erwartet Warnung)."""
    data = setup_db_for_combined
    # Kosten und Prozente sind hier irrelevant für den Test der Summenprüfung
    rules = [
        {'cost_type_id': data['ct_consum_id'], 'percentage': 40.0, 'total_cost_part': 400, 'period_start': date(2023, 7, 1), 'period_end': date(2023, 7, 31)},
        {'cost_type_id': data['ct_share_id'], 'percentage': 50.0, 'total_cost_part': 500}
    ]
    # Hier testen wir nicht das Ergebnis, nur dass die Funktion läuft und keine Exception wirft
    # (Die Warnung wird auf stdout ausgegeben, was hier nicht leicht zu testen ist)
    allocation = calculate_combined_allocation(rules)
    assert allocation is not None 

def test_combined_allocation_invalid_rule(setup_db_for_combined):
    """Testet eine Regel mit fehlenden Schlüsseln."""
    data = setup_db_for_combined
    rules = [
        {'cost_type_id': data['ct_share_id'], 'percentage': 100.0} # total_cost_part fehlt
    ]
    allocation = calculate_combined_allocation(rules)
    # Erwartet, dass die Regel übersprungen wird und das Ergebnis leer ist
    assert allocation is not None
    assert len(allocation) == 0

def test_combined_allocation_empty_rules():
     """Testet den Aufruf mit einer leeren Regel-Liste."""
     allocation = calculate_combined_allocation([])
     assert allocation == {} 
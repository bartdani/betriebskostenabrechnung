import pytest
import io
from app.models import Apartment, CostType, ConsumptionData
from app.import_data import import_consumption_csv

# Die Fixture 'test_db' wird aus conftest.py verwendet.

@pytest.fixture
def setup_db_for_import(test_db):
    """Erstellt notwendige Stammdaten für Import-Tests."""
    a1 = Apartment(number='Top 1')
    a2 = Apartment(number='Top 2')
    ct_heiz = CostType(name='Heizung', unit='kWh', type='consumption')
    ct_wasser = CostType(name='Wasser', unit='m³', type='consumption')
    test_db.session.add_all([a1, a2, ct_heiz, ct_wasser])
    test_db.session.commit()
    return test_db # Gibt die konfigurierte DB zurück

def test_csv_import_valid_data(setup_db_for_import):
    """Testet den Import einer CSV mit ausschließlich validen Daten."""
    test_db = setup_db_for_import
    csv_data = (
        "apartment_number,cost_type_name,date,value\n"
        "Top 1,Heizung,2023-01-15,150.5\n"
        "Top 2,Wasser,2023-01-16,25.8\n"
        "Top 1,Wasser,2023-02-01,30.1"
    )
    csv_stream = io.StringIO(csv_data)
    
    result = import_consumption_csv(csv_stream)
    
    assert result['processed_rows'] == 3
    assert result['skipped_rows'] == 0
    
    # Überprüfen, ob die Daten korrekt in der DB sind
    data = ConsumptionData.query.order_by(ConsumptionData.date).all()
    assert len(data) == 3
    assert data[0].apartment.number == 'Top 1'
    assert data[0].cost_type.name == 'Heizung'
    assert data[0].value == 150.5
    assert data[1].apartment.number == 'Top 2'
    assert data[1].cost_type.name == 'Wasser'
    assert data[1].value == 25.8
    assert data[2].apartment.number == 'Top 1'
    assert data[2].cost_type.name == 'Wasser'
    assert data[2].value == 30.1

def test_csv_import_with_invalid_data(setup_db_for_import):
    """Testet den Import einer CSV mit validen und invaliden Daten."""
    test_db = setup_db_for_import
    csv_data = (
        "apartment_number,cost_type_name,date,value\n"
        "Top 1,Heizung,2023-03-10,200.0\n"       # Valid
        "Top 3,Heizung,2023-03-11,50.0\n"        # Invalid: Apartment not found
        "Top 1,Strom,2023-03-12,75.0\n"         # Invalid: CostType not found
        "Top 2,Wasser,2023-13-01,10.0\n"        # Invalid: Date format
        "Top 1,Wasser,2023-03-14,abc\n"         # Invalid: Value format
        "Top 2,Heizung,2023-03-15,220.0\n"       # Valid
        "Top 1,Heizung\n"                       # Invalid: Missing columns
    )
    csv_stream = io.StringIO(csv_data)
    
    result = import_consumption_csv(csv_stream)
    
    assert result['processed_rows'] == 2 # Nur die zwei validen Zeilen
    assert result['skipped_rows'] == 5 # Fünf invalide Zeilen
    
    # Überprüfen, ob nur die validen Daten in der DB sind
    data = ConsumptionData.query.order_by(ConsumptionData.date).all()
    assert len(data) == 2
    assert data[0].apartment.number == 'Top 1'
    assert data[0].cost_type.name == 'Heizung'
    assert data[0].value == 200.0
    assert data[1].apartment.number == 'Top 2'
    assert data[1].cost_type.name == 'Heizung'
    assert data[1].value == 220.0

def test_csv_import_missing_header(setup_db_for_import):
    """Testet den Import einer CSV mit fehlenden Headern."""
    test_db = setup_db_for_import
    csv_data = (
        "apartment_number,cost_type_name,date\n" # Fehlender 'value' Header
        "Top 1,Heizung,2023-04-01"
    )
    csv_stream = io.StringIO(csv_data)
    
    result = import_consumption_csv(csv_stream)
    
    assert result['processed_rows'] == 0 
    assert result['skipped_rows'] == -1 # Spezialwert für Header-Fehler
    assert ConsumptionData.query.count() == 0 # Nichts importiert 
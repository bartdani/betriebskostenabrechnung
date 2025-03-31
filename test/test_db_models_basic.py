import pytest
from app.models import Apartment, Tenant, CostType, ConsumptionData
from datetime import datetime

# Die Fixtures 'app_context' und 'test_db' werden aus conftest.py verwendet.

def test_create_apartment(test_db):
    """Testet das Erstellen und Speichern eines Apartment-Objekts."""
    a = Apartment(number='Top 1')
    test_db.session.add(a)
    test_db.session.commit()
    
    retrieved_a = Apartment.query.filter_by(number='Top 1').first()
    assert retrieved_a is not None
    assert retrieved_a.number == 'Top 1'

def test_create_tenant(test_db):
    """Testet das Erstellen und Speichern eines Tenant-Objekts mit Apartment-Beziehung."""
    a = Apartment(number='Top 2')
    t = Tenant(name='Max Mustermann', contact_info='max@test.com', apartment=a)
    test_db.session.add(a) # Muss auch hinzugefügt werden, da Beziehung besteht
    test_db.session.add(t)
    test_db.session.commit()
    
    retrieved_t = Tenant.query.filter_by(name='Max Mustermann').first()
    assert retrieved_t is not None
    assert retrieved_t.name == 'Max Mustermann'
    assert retrieved_t.apartment is not None
    assert retrieved_t.apartment.number == 'Top 2'

def test_create_cost_type(test_db):
    """Testet das Erstellen und Speichern eines CostType-Objekts."""
    ct = CostType(name='Heizung', unit='kWh', type='consumption')
    test_db.session.add(ct)
    test_db.session.commit()
    
    retrieved_ct = CostType.query.filter_by(name='Heizung').first()
    assert retrieved_ct is not None
    assert retrieved_ct.unit == 'kWh'
    assert retrieved_ct.type == 'consumption'

def test_create_consumption_data(test_db):
    """Testet das Erstellen und Speichern eines ConsumptionData-Objekts mit Beziehungen."""
    a = Apartment(number='Top 3')
    ct = CostType(name='Wasser', unit='m³', type='consumption')
    test_db.session.add_all([a, ct])
    test_db.session.commit()
    
    # Holen der IDs, nachdem sie committet wurden
    apt_id = a.id
    ct_id = ct.id
    
    # Neues ConsumptionData-Objekt erstellen
    cd = ConsumptionData(apartment_id=apt_id, cost_type_id=ct_id, value=123.45)
    # Standard-Datum wird verwendet
    test_db.session.add(cd)
    test_db.session.commit()
    
    retrieved_cd = ConsumptionData.query.filter_by(value=123.45).first()
    assert retrieved_cd is not None
    assert retrieved_cd.apartment_id == apt_id
    assert retrieved_cd.cost_type_id == ct_id
    assert isinstance(retrieved_cd.date, datetime) 
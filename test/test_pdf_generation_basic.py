import pytest
from datetime import date
import io

from app import db
from app.models import Tenant, Apartment, Contract, CostType, ApartmentShare, OccupancyPeriod
from app.pdf_generation import generate_utility_statement_pdf

# Helper function to create dummy data
def create_test_data():
    # Create Apartment
    apt1 = Apartment(number='WE01', address='Teststraße 1', size_sqm=50.0)
    db.session.add(apt1)
    db.session.flush() # Get ID for foreign keys

    # Create Tenant (ohne apartment_id)
    t1 = Tenant(
        name='Test Tenant',
        contact_info='Test Street 1\n12345 Test City'
    )
    db.session.add(t1)
    db.session.flush()

    # Create Contract (Verknüpft Tenant und Apartment)
    c1 = Contract(
        tenant_id=t1.id,
        apartment_id=apt1.id,
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31),
        rent_amount=500.0
    )
    db.session.add(c1)
    db.session.flush()

    # Create CostTypes
    ct_share = CostType(name='Grundsteuer', unit='m²', type='share')
    ct_consum = CostType(name='Wasser', unit='m³', type='consumption')
    ct_person = CostType(name='Müll', unit='Pers.', type='person_days')
    db.session.add_all([ct_share, ct_consum, ct_person])
    db.session.flush()

    # Create ApartmentShare
    share1 = ApartmentShare(
        apartment_id=apt1.id,
        cost_type_id=ct_share.id,
        value=75.0
    )
    db.session.add(share1)

    # Create OccupancyPeriod
    occ1 = OccupancyPeriod(
        apartment_id=apt1.id,
        start_date=date(2023,1,1),
        end_date=date(2023, 12, 31),
        number_of_occupants=2
    )
    db.session.add(occ1)
    
    # Dummy Consumption Data (nicht unbedingt nötig für PDF-Test, da Allocation separat getestet)
    # cons1 = ConsumptionData(apartment_id=apt1.id, cost_type_id=ct_consum.id, date=date(2023, 6, 15), value=10.0)
    # db.session.add(cons1)

    db.session.commit()
    return apt1.id, t1.id, c1.id, ct_share.id, ct_consum.id, ct_person.id

def test_generate_pdf_basic(test_db, client):
    """Testet, ob die PDF-Generierung grundsätzlich einen Byte-Stream zurückgibt."""
    apt_id, t_id, c_id, ct_s_id, ct_c_id, ct_p_id = create_test_data()
    
    period_start = date(2023, 1, 1)
    period_end = date(2023, 12, 31)
    
    # Beispielhafte Kostenpositionen (Gesamtkosten für das Haus)
    cost_items = [
        {'cost_type_id': ct_s_id, 'total_cost': 250.50},
        {'cost_type_id': ct_c_id, 'total_cost': 180.75},
        {'cost_type_id': ct_p_id, 'total_cost': 95.00}
    ]

    pdf_bytes = generate_utility_statement_pdf(c_id, period_start, period_end, cost_items)

    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 100 # Prüft, ob mehr als nur ein leerer Header generiert wurde

    # Optional: Überprüfen, ob es sich um ein PDF handelt (rudimentär)
    # PDF-Dateien beginnen normalerweise mit '%PDF'
    assert pdf_bytes.startswith(b'%PDF') 
from datetime import date, datetime
from app import db
from app.models import Apartment, Tenant, Contract, CostType, ConsumptionData
from app.pdf_generation import generate_utility_statement_pdf


def create_test_data_heating():
    # Stammdaten
    apt = Apartment(number='PDF-H-1', address='PDF Heat Str 1', size_sqm=70.0)
    tenant = Tenant(name='PDF Heizkunde', contact_info='pdf@kunde.local')
    db.session.add_all([apt, tenant])
    db.session.commit()

    contract = Contract(tenant_id=tenant.id, apartment_id=apt.id, start_date=date(2024, 1, 1), rent_amount=800.0)
    db.session.add(contract)
    db.session.commit()

    # Kostenarten: Heizung/Warmwasser als Verbrauchstypen
    ct_heat = CostType(name='Heizenergie-PDF', unit='kWh', type='consumption')
    ct_hot = CostType(name='Warmwasser-PDF', unit='m³', type='consumption')
    db.session.add_all([ct_heat, ct_hot])
    db.session.commit()

    # Verbrauchsdaten für die Wohnung
    db.session.add_all([
        ConsumptionData(apartment_id=apt.id, cost_type_id=ct_hot.id, date=datetime(2024, 1, 5), value=20.0),
        ConsumptionData(apartment_id=apt.id, cost_type_id=ct_heat.id, date=datetime(2024, 1, 10), value=150.0),
    ])
    db.session.commit()

    return contract, ct_heat, ct_hot


def test_generate_pdf_with_heating_item(client):
    contract, ct_heat, ct_hot = create_test_data_heating()
    cost_items = [
        {
            'type': 'heating',
            'total_cost': 500.0,
            'hot_water_percentage': 30.0,
            'heating_consumption_cost_type_id': ct_heat.id,
            'hot_water_consumption_cost_type_id': ct_hot.id,
        }
    ]

    pdf_bytes = generate_utility_statement_pdf(
        contract_id=contract.id,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        cost_items=cost_items,
    )

    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b'%PDF')



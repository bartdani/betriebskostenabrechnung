from datetime import date, datetime
from app import create_app, db
from app.models import Apartment, Tenant, Contract, CostType, ConsumptionData, ApartmentShare, OccupancyPeriod, Meter, Invoice


def _get_or_create_apartment(number: str, address: str, size_sqm: float) -> Apartment:
    apt = Apartment.query.filter_by(number=number).first()
    if apt:
        return apt
    apt = Apartment(number=number, address=address, size_sqm=size_sqm)
    db.session.add(apt)
    db.session.flush()
    return apt


def _get_or_create_tenant(name: str, contact: str) -> Tenant:
    t = Tenant.query.filter_by(name=name).first()
    if t:
        return t
    t = Tenant(name=name, contact_info=contact)
    db.session.add(t)
    db.session.flush()
    return t


def _get_or_create_contract(tenant_id: int, apartment_id: int, start: date, rent_amount: float) -> Contract:
    c = Contract.query.filter_by(tenant_id=tenant_id, apartment_id=apartment_id, start_date=start).first()
    if c:
        return c
    c = Contract(tenant_id=tenant_id, apartment_id=apartment_id, start_date=start, rent_amount=rent_amount)
    db.session.add(c)
    db.session.flush()
    return c


def _get_or_create_cost_type(name: str, unit: str, ctype: str) -> CostType:
    ct = CostType.query.filter_by(name=name).first()
    if ct:
        return ct
    ct = CostType(name=name, unit=unit, type=ctype)
    db.session.add(ct)
    db.session.flush()
    return ct


def _get_or_create_share(apartment_id: int, cost_type_id: int, value: float) -> ApartmentShare:
    s = ApartmentShare.query.filter_by(apartment_id=apartment_id, cost_type_id=cost_type_id).first()
    if s:
        return s
    s = ApartmentShare(apartment_id=apartment_id, cost_type_id=cost_type_id, value=value)
    db.session.add(s)
    db.session.flush()
    return s


def _ensure_occupancy(apartment_id: int, start: date, end: date | None, num: int):
    exists = OccupancyPeriod.query.filter_by(apartment_id=apartment_id, start_date=start, end_date=end, number_of_occupants=num).first()
    if not exists:
        db.session.add(OccupancyPeriod(apartment_id=apartment_id, start_date=start, end_date=end, number_of_occupants=num))


def _get_or_create_meter(apartment_id: int, meter_type: str, serial: str, unit: str) -> Meter:
    m = Meter.query.filter_by(serial_number=serial).first()
    if m:
        return m
    m = Meter(apartment_id=apartment_id, meter_type=meter_type, serial_number=serial, unit=unit)
    db.session.add(m)
    db.session.flush()
    return m


def _ensure_consumption(apartment_id: int, cost_type_id: int, dt: datetime, value: float, entry_type: str = 'csv_import'):
    exists = ConsumptionData.query.filter_by(apartment_id=apartment_id, cost_type_id=cost_type_id, date=dt, value=value).first()
    if not exists:
        db.session.add(ConsumptionData(apartment_id=apartment_id, cost_type_id=cost_type_id, date=dt, value=value, entry_type=entry_type))


def _get_or_create_invoice(number: str, date_: date, amount: float, cost_type_id: int, ps: date, pe: date, direct_contract_id: int | None = None) -> Invoice:
    inv = Invoice.query.filter_by(invoice_number=number).first()
    if inv:
        return inv
    inv = Invoice(invoice_number=number, date=date_, amount=amount, cost_type_id=cost_type_id, period_start=ps, period_end=pe, direct_allocation_contract_id=direct_contract_id)
    db.session.add(inv)
    db.session.flush()
    return inv


def seed():
    # Wohnungen
    apt1 = _get_or_create_apartment('WE01', 'Hauptstraße 1, Top 1', 50.0)
    apt2 = _get_or_create_apartment('WE02', 'Hauptstraße 1, Top 2', 65.0)

    # Mieter
    t1 = _get_or_create_tenant('Max Mustermann', 'max@example.com')
    t2 = _get_or_create_tenant('Erika Musterfrau', 'erika@example.com')

    # Verträge
    c1 = _get_or_create_contract(t1.id, apt1.id, date(2024, 1, 1), 600.0)
    c2 = _get_or_create_contract(t2.id, apt2.id, date(2024, 1, 1), 800.0)

    # Kostenarten
    ct_water = _get_or_create_cost_type('Kaltwasser', 'm³', 'consumption')
    ct_heat = _get_or_create_cost_type('Heizung', 'kWh', 'consumption')
    ct_hot = _get_or_create_cost_type('Warmwasser', 'm³', 'consumption')
    ct_trash = _get_or_create_cost_type('Müll', 'Pers.', 'person_days')
    ct_tax = _get_or_create_cost_type('Grundsteuer', 'm²', 'share')

    # Anteile (ApartmentShare) für Grundsteuer (m²)
    _get_or_create_share(apt1.id, ct_tax.id, apt1.size_sqm)
    _get_or_create_share(apt2.id, ct_tax.id, apt2.size_sqm)

    # Belegungsperioden 2024 (2 Personen in WE02 ab Juli)
    _ensure_occupancy(apt1.id, date(2024, 1, 1), date(2024, 12, 31), 1)
    _ensure_occupancy(apt2.id, date(2024, 1, 1), date(2024, 6, 30), 1)
    _ensure_occupancy(apt2.id, date(2024, 7, 1), date(2024, 12, 31), 2)

    # Zähler pro Wohnung
    m_we01_water = _get_or_create_meter(apt1.id, 'Wasser', 'WE01-W-001', 'm³')
    m_we01_heat = _get_or_create_meter(apt1.id, 'Heizung', 'WE01-H-001', 'kWh')
    m_we01_hot = _get_or_create_meter(apt1.id, 'Warmwasser', 'WE01-HW-001', 'm³')
    m_we02_water = _get_or_create_meter(apt2.id, 'Wasser', 'WE02-W-001', 'm³')
    m_we02_heat = _get_or_create_meter(apt2.id, 'Heizung', 'WE02-H-001', 'kWh')
    m_we02_hot = _get_or_create_meter(apt2.id, 'Warmwasser', 'WE02-HW-001', 'm³')

    # Verbrauchsdaten (einige Werte, dienen als Zählerstände/Verbräuche)
    _ensure_consumption(apt1.id, ct_water.id, datetime(2024, 1, 15), 12.0)
    _ensure_consumption(apt1.id, ct_water.id, datetime(2024, 6, 15), 14.5)
    _ensure_consumption(apt1.id, ct_heat.id, datetime(2024, 1, 20), 180.0)
    _ensure_consumption(apt1.id, ct_heat.id, datetime(2024, 3, 20), 160.0)
    _ensure_consumption(apt1.id, ct_hot.id, datetime(2024, 2, 10), 8.0)
    _ensure_consumption(apt1.id, ct_hot.id, datetime(2024, 8, 10), 9.0)

    _ensure_consumption(apt2.id, ct_water.id, datetime(2024, 1, 12), 15.0)
    _ensure_consumption(apt2.id, ct_water.id, datetime(2024, 6, 12), 17.0)
    _ensure_consumption(apt2.id, ct_heat.id, datetime(2024, 1, 22), 220.0)
    _ensure_consumption(apt2.id, ct_heat.id, datetime(2024, 3, 22), 210.0)
    _ensure_consumption(apt2.id, ct_hot.id, datetime(2024, 2, 12), 10.0)
    _ensure_consumption(apt2.id, ct_hot.id, datetime(2024, 8, 12), 11.0)

    # Rechnungen (verteilt)
    _get_or_create_invoice('W-2024-001', date(2024, 12, 15), 400.0, ct_water.id, date(2024, 1, 1), date(2024, 12, 31))
    _get_or_create_invoice('H-2024-001', date(2024, 12, 15), 2000.0, ct_heat.id, date(2024, 1, 1), date(2024, 12, 31))
    _get_or_create_invoice('HW-2024-001', date(2024, 12, 15), 600.0, ct_hot.id, date(2024, 1, 1), date(2024, 12, 31))
    _get_or_create_invoice('T-2024-001', date(2024, 12, 15), 300.0, ct_trash.id, date(2024, 1, 1), date(2024, 12, 31))
    _get_or_create_invoice('G-2024-001', date(2024, 12, 15), 800.0, ct_tax.id, date(2024, 1, 1), date(2024, 12, 31))

    # Direkte Zuordnung (z. B. Schornsteinfeger nur für eine Wohnung)
    _get_or_create_invoice('D-2024-001', date(2024, 6, 1), 120.0, ct_heat.id, date(2024, 5, 1), date(2024, 5, 31), direct_contract_id=c1.id)
    _get_or_create_invoice('D-2024-002', date(2024, 7, 1), 90.0, ct_water.id, date(2024, 6, 1), date(2024, 6, 30), direct_contract_id=c2.id)

    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed()
        print('Demo-Daten wurden angelegt.')



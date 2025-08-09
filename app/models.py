from app import db
from datetime import datetime
from sqlalchemy import CheckConstraint, event
from sqlalchemy.orm import validates

class Building(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.String(500), nullable=True)

    apartments = db.relationship('Apartment', backref='building', lazy='dynamic')

    def __repr__(self):
        return f'<Building {self.name}>'


class Apartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), index=True, unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False) # NEU: Adresse der Wohnung
    size_sqm = db.Column(db.Float, nullable=False) # NEU: Größe in Quadratmetern
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=True)
    contracts = db.relationship('Contract', backref='apartment', lazy='dynamic')
    consumption_data = db.relationship('ConsumptionData', backref='apartment', lazy='dynamic')
    shares = db.relationship('ApartmentShare', backref='apartment', lazy='dynamic', cascade="all, delete-orphan")
    occupancy_periods = db.relationship('OccupancyPeriod', backref='apartment', lazy='dynamic', cascade="all, delete-orphan")
    meters = db.relationship('Meter', backref='apartment', lazy='dynamic', cascade="all, delete-orphan") # NEU: Beziehung zu Zählern

    def __repr__(self):
        return f'<Apartment {self.number}>'

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(200)) # Z.B. E-Mail, Telefon
    contracts = db.relationship('Contract', backref='tenant', lazy='dynamic')

    def __repr__(self):
        return f'<Tenant {self.name}>'

class CostType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    unit = db.Column(db.String(20), nullable=False) # z.B. 'm²', 'kWh', 'm³', 'Einheiten'
    type = db.Column(db.String(20), nullable=False) # 'consumption' oder 'share'
    consumption_data = db.relationship('ConsumptionData', backref='cost_type', lazy='dynamic')
    apartment_shares = db.relationship('ApartmentShare', backref='cost_type', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<CostType {self.name} ({self.type})>'

class ConsumptionData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)
    cost_type_id = db.Column(db.Integer, db.ForeignKey('cost_type.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Float, nullable=False)
    entry_type = db.Column(db.String(20), nullable=False, default='csv_import', server_default='csv_import') # csv_import, manual

    def __repr__(self):
        return f'<ConsumptionData Apt:{self.apartment_id} Type:{self.cost_type_id} Date:{self.date} Val:{self.value}>'

# NEUES MODELL: Contract
class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True) # Kann unbefristet sein

    rent_amount = db.Column(db.Float, nullable=False) # Aktueller Mietzins

    # Indexklausel - Basisinformationen
    # Genauere Implementierung der Indexlogik folgt später
    index_clause_base_value = db.Column(db.Float, nullable=True) # z.B. VPI-Wert
    index_clause_base_date = db.Column(db.Date, nullable=True) # Datum des Basiswerts

    # NEU: Dateiname des gespeicherten Vertrags-PDFs
    contract_pdf_filename = db.Column(db.String(255), nullable=True)

    # NEU: Beziehung zu direkt zugeordneten Rechnungen
    direct_allocation_invoices = db.relationship('Invoice', backref='direct_allocation_contract', lazy='dynamic', foreign_keys='Invoice.direct_allocation_contract_id')

    # Später: Referenz auf Kostenverteilschlüssel-Profil
    # cost_allocation_profile_id = db.Column(db.Integer, db.ForeignKey('cost_allocation_profile.id'))

    # Sicherstellen, dass Enddatum nach Startdatum liegt (falls vorhanden)
    __table_args__ = (
        CheckConstraint('end_date IS NULL OR end_date > start_date', name='check_contract_dates'),
    )

    def __repr__(self):
        tenant_name = self.tenant.name if self.tenant else 'N/A'
        apt_number = self.apartment.number if self.apartment else 'N/A'
        return f'<Contract Apt:{apt_number} Tenant:{tenant_name} Start:{self.start_date}>'

# NEUES MODELL: ApartmentShare
class ApartmentShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)
    cost_type_id = db.Column(db.Integer, db.ForeignKey('cost_type.id'), nullable=False)
    value = db.Column(db.Float, nullable=False) # z.B. Quadratmeter, Personenanzahl

    # Optional: Gültigkeitszeitraum für den Anteilswert
    # valid_from = db.Column(db.Date)
    # valid_to = db.Column(db.Date)

    # Index, um schnelle Suche pro Apartment/CostType zu ermöglichen
    __table_args__ = (db.UniqueConstraint('apartment_id', 'cost_type_id', name='uq_apartment_cost_type_share'),)

    @validates('cost_type')
    def validate_cost_type_is_share(self, key, cost_type_obj):
        """Stellt sicher, dass nur CostTypes vom Typ 'share' verknüpft werden."""
        if cost_type_obj and cost_type_obj.type != 'share':
            raise ValueError(f"CostType '{cost_type_obj.name}' must be of type 'share' to be used in ApartmentShare.")
        return cost_type_obj

    def __repr__(self):
        apt_number = self.apartment.number if self.apartment else 'N/A'
        ct_name = self.cost_type.name if self.cost_type else 'N/A'
        return f'<ApartmentShare Apt:{apt_number} CostType:{ct_name} Value:{self.value}>'

# Event Listener (alternativ zu @validates, fängt Zuweisung der ID ab)
# Deaktiviert, da @validates auf das Objekt präferiert wird, wenn möglich.
# @event.listens_for(ApartmentShare.cost_type_id, 'set', retval=True)
# def validate_cost_type_id_is_share(target, value, oldvalue, initiator):
#     """Stellt sicher, dass die cost_type_id zu einem 'share' Typ gehört."""
#     if value is not None:
#         cost_type = db.session.get(CostType, value)
#         if cost_type and cost_type.type != 'share':
#             raise ValueError(f"CostType ID {value} must be of type 'share' to be used in ApartmentShare.")
#     return value

# NEUES MODELL: OccupancyPeriod
class OccupancyPeriod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=True, index=True) # NULL bedeutet bis auf weiteres
    number_of_occupants = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        CheckConstraint('end_date IS NULL OR end_date > start_date', name='check_occupancy_period_dates'),
        CheckConstraint('number_of_occupants > 0', name='check_positive_occupants'),
        # Optional: Constraint, um Überlappungen pro Wohnung zu verhindern (komplexer, evtl. später)
    )

    def __repr__(self):
        apt_number = self.apartment.number if self.apartment else 'N/A'
        end_str = str(self.end_date) if self.end_date else 'ongoing'
        return f'<OccupancyPeriod Apt:{apt_number} Occupants:{self.number_of_occupants} Start:{self.start_date} End:{end_str}>'

# NEUES MODELL: Meter
class Meter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False, index=True)
    meter_type = db.Column(db.String(50), nullable=False) # z.B. 'Strom', 'Wasser', 'Heizung', 'Warmwasser'
    serial_number = db.Column(db.String(100), nullable=False, unique=True)
    unit = db.Column(db.String(20), nullable=False) # z.B. 'kWh', 'm³'

    # Beziehung zu Apartment wird über backref='meters' in Apartment definiert

    def __repr__(self):
        apt_number = self.apartment.number if self.apartment else 'N/A'
        return f'<Meter {self.serial_number} ({self.meter_type}) Apt:{apt_number}>'

# NEUES MODELL: Invoice
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(100), nullable=True, index=True) # Rechnungsnummer
    date = db.Column(db.Date, nullable=False, index=True) # Rechnungsdatum
    amount = db.Column(db.Float, nullable=False) # Rechnungsbetrag
    cost_type_id = db.Column(db.Integer, db.ForeignKey('cost_type.id'), nullable=False, index=True) # FK zur Kostenart
    period_start = db.Column(db.Date, nullable=False) # Leistungszeitraum Start
    period_end = db.Column(db.Date, nullable=False) # Leistungszeitraum Ende

    # Für direkte Zuordnung (sonst NULL)
    direct_allocation_contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=True, index=True)
    # Gebäude-Kontext für saubere Aggregation (optional, initial nullable für Abwärtskompatibilität)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=True, index=True)

    # Beziehung zu CostType
    cost_type = db.relationship('CostType', backref='invoices')
    building = db.relationship('Building', backref='invoices')
    # Beziehung zu Contract (für direkte Zuordnung) ist über backref='direct_allocation_invoices' in Contract definiert

    # Sicherstellen, dass Enddatum nach Startdatum liegt
    __table_args__ = (
        CheckConstraint('period_end >= period_start', name='check_invoice_period_dates'),
    )

    def __repr__(self):
        allocation_type = f"Contract:{self.direct_allocation_contract_id}" if self.direct_allocation_contract_id else "Distributed"
        ct_name = self.cost_type.name if self.cost_type else 'N/A'
        return f'<Invoice {self.id} Date:{self.date} Amount:{self.amount} CostType:{ct_name} Allocation:{allocation_type}>' 
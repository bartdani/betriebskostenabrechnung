from app import db
from datetime import datetime
from sqlalchemy import CheckConstraint

class Apartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), index=True, unique=True, nullable=False)
    # Weitere Felder wie Größe, Adresse etc. können hier hinzugefügt werden
    tenants = db.relationship('Tenant', backref='apartment', lazy='dynamic')
    contracts = db.relationship('Contract', backref='apartment', lazy='dynamic')
    consumption_data = db.relationship('ConsumptionData', backref='apartment', lazy='dynamic')

    def __repr__(self):
        return f'<Apartment {self.number}>'

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(200)) # Z.B. E-Mail, Telefon
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'))
    # Mietvertragsdaten könnten hier oder in einer separaten Tabelle stehen
    contracts = db.relationship('Contract', backref='tenant', lazy='dynamic')

    def __repr__(self):
        return f'<Tenant {self.name}>'

class CostType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    unit = db.Column(db.String(20), nullable=False) # z.B. 'm²', 'kWh', 'm³', 'Einheiten'
    type = db.Column(db.String(20), nullable=False) # 'consumption' oder 'share'
    consumption_data = db.relationship('ConsumptionData', backref='cost_type', lazy='dynamic')

    def __repr__(self):
        return f'<CostType {self.name} ({self.type})>'

class ConsumptionData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)
    cost_type_id = db.Column(db.Integer, db.ForeignKey('cost_type.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    value = db.Column(db.Float, nullable=False)
    # Optional: Feld für Zählerstände (Start/End) statt nur Verbrauchswert

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
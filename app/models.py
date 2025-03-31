from app import db
from datetime import datetime

class Apartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), index=True, unique=True, nullable=False)
    # Weitere Felder wie Größe, Adresse etc. können hier hinzugefügt werden
    tenants = db.relationship('Tenant', backref='apartment', lazy='dynamic')
    consumption_data = db.relationship('ConsumptionData', backref='apartment', lazy='dynamic')

    def __repr__(self):
        return f'<Apartment {self.number}>'

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(200)) # Z.B. E-Mail, Telefon
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'))
    # Mietvertragsdaten könnten hier oder in einer separaten Tabelle stehen

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
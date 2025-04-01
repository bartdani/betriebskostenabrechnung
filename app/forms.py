from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DateField, FloatField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from app import db
from app.models import CostType

class CostTypeForm(FlaskForm):
    """Formular zum Erstellen und Bearbeiten von Kostenarten."""
    name = StringField('Name der Kostenart', 
                       validators=[DataRequired(), Length(min=2, max=100)],
                       render_kw={"placeholder": "z.B. Kaltwasser, Heizfläche"})
    unit = StringField('Einheit', 
                       validators=[DataRequired(), Length(max=20)],
                       render_kw={"placeholder": "z.B. m³, kWh, m²"})
    type = SelectField('Verteilungsart', 
                       choices=[('consumption', 'Verbrauchsbasiert'), ('share', 'Anteilsbasiert')],
                       validators=[DataRequired()])
    submit = SubmitField('Speichern')

class ManualConsumptionForm(FlaskForm):
    apartment_id = SelectField('Wohnung', coerce=int, validators=[DataRequired()])
    cost_type_id = SelectField('Kostenart (Verbrauch)', coerce=int, validators=[DataRequired()])
    date = DateField('Datum', validators=[DataRequired()], format='%Y-%m-%d')
    value = FloatField('Zählerstand / Wert', validators=[DataRequired()])
    submit = SubmitField('Speichern')

    def validate_cost_type_id(self, field):
        """Validiert, dass die ausgewählte Kostenart vom Typ 'consumption' ist."""
        cost_type = db.session.get(CostType, field.data)
        if not cost_type or cost_type.type != 'consumption':
            raise ValidationError('Ungültige Kostenart ausgewählt.') 
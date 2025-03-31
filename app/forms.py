from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

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
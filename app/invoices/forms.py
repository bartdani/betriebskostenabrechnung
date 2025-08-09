from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, FloatField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Optional, NumberRange


class InvoiceForm(FlaskForm):
    invoice_number = StringField('Rechnungsnummer', validators=[Optional()])
    date = DateField('Rechnungsdatum', format='%Y-%m-%d', validators=[DataRequired()])
    amount = FloatField('Betrag', validators=[DataRequired(message='Betrag ist erforderlich'), NumberRange(min=0.01)])
    cost_type_id = SelectField('Kostenart', coerce=int, validators=[DataRequired()])
    period_start = DateField('Leistungszeitraum Start', format='%Y-%m-%d', validators=[DataRequired()])
    period_end = DateField('Leistungszeitraum Ende', format='%Y-%m-%d', validators=[DataRequired()])
    direct_allocation_contract_id = SelectField('Direkte Zuordnung (optional)', coerce=int, validators=[Optional()])
    submit = SubmitField('Speichern')

    def validate(self, extra_validators=None):
        is_valid = super().validate(extra_validators=extra_validators)
        # Zusätzliche Feldübergreifende Validierung für Zeitraum
        if self.period_start.data and self.period_end.data:
            if self.period_end.data < self.period_start.data:
                self.period_end.errors.append('Ende muss nach Start liegen')
                is_valid = False
        return is_valid



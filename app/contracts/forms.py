from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, FloatField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Optional, NumberRange


class ContractForm(FlaskForm):
    tenant_id = SelectField('Mieter', coerce=int, validators=[DataRequired()])
    apartment_id = SelectField('Wohnung', coerce=int, validators=[DataRequired()])
    start_date = DateField('Startdatum', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('Enddatum', format='%Y-%m-%d', validators=[Optional()])
    rent_amount = FloatField('Mietzins', validators=[DataRequired(message='Mietzins ist erforderlich'), NumberRange(min=0.01)])
    submit = SubmitField('Speichern')

    def validate(self, extra_validators=None):
        is_valid = super().validate(extra_validators=extra_validators)
        if self.start_date.data and self.end_date.data:
            if self.end_date.data <= self.start_date.data:
                # Konsistent zu DB-Constraint: muss > sein
                self.end_date.errors.append('Ende muss nach Start liegen')
                is_valid = False
        return is_valid



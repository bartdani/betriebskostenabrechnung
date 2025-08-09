from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, HiddenField, DateField, FloatField
from wtforms.validators import DataRequired, Length


class MeterForm(FlaskForm):
    meter_type = StringField('Zählertyp', validators=[
        DataRequired(message='Zählertyp ist erforderlich'),
        Length(max=50, message='Zählertyp darf maximal 50 Zeichen lang sein')
    ])
    serial_number = StringField('Seriennummer', validators=[
        DataRequired(message='Seriennummer ist erforderlich'),
        Length(max=100, message='Seriennummer darf maximal 100 Zeichen lang sein')
    ])
    unit = StringField('Einheit', validators=[
        DataRequired(message='Einheit ist erforderlich'),
        Length(max=20, message='Einheit darf maximal 20 Zeichen lang sein')
    ])
    apartment_id = SelectField('Wohnung', coerce=int, validators=[DataRequired(message='Wohnung ist erforderlich')])

    # Optional: für Templates, um zwischen Neu/Bearbeiten zu unterscheiden
    instance_id = HiddenField()

    submit = SubmitField('Speichern')


class MeterReadingForm(FlaskForm):
    meter_id = SelectField('Zähler', coerce=int, validators=[DataRequired()])
    date = DateField('Datum', validators=[DataRequired()], format='%Y-%m-%d')
    value = FloatField('Wert', validators=[DataRequired()])
    submit = SubmitField('Speichern')


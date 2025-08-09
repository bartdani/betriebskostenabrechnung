from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, InputRequired, Optional, Length, NumberRange
from wtforms.fields import DateField

class ApartmentForm(FlaskForm):
    number = StringField('Wohnungsnummer', validators=[
        DataRequired(message="Bitte geben Sie eine Wohnungsnummer ein."), 
        Length(min=1, max=50, message="Die Wohnungsnummer darf maximal 50 Zeichen lang sein.")
    ])
    address = StringField('Adresse', validators=[
        DataRequired(message="Bitte geben Sie eine Adresse ein."),
        Length(min=5, max=200, message="Die Adresse muss zwischen 5 und 200 Zeichen lang sein.")
    ])
    size_sqm = FloatField('Größe (m²)', validators=[
        DataRequired(message="Bitte geben Sie die Größe ein."),
        NumberRange(min=0.1, message="Die Größe muss ein positiver Wert sein.")
    ])
    building_id = SelectField('Gebäude', coerce=int, validators=[Optional()], validate_choice=False)
    submit = SubmitField('Speichern') 


class OccupancyPeriodForm(FlaskForm):
    start_date = DateField('Startdatum', format='%Y-%m-%d', validators=[
        DataRequired(message='Startdatum ist erforderlich')
    ])
    end_date = DateField('Enddatum', format='%Y-%m-%d', validators=[Optional()], default=None)
    number_of_occupants = IntegerField('Anzahl der Bewohner', validators=[
        InputRequired(message='Anzahl der Bewohner ist erforderlich'),
        NumberRange(min=1, message='Anzahl der Bewohner muss > 0 sein')
    ])
    submit = SubmitField('Speichern')
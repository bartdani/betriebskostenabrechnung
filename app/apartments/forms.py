from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

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
    submit = SubmitField('Speichern') 
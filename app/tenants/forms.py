from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length

class TenantForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(message='Name ist erforderlich'),
        Length(max=100, message='Name darf maximal 100 Zeichen lang sein')
    ])
    contact_info = StringField('Kontaktinfo', validators=[
        Length(max=200, message='Kontaktinfo darf maximal 200 Zeichen lang sein')
    ])
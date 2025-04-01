from flask import Blueprint

apartments_bp = Blueprint('apartments', __name__, template_folder='../templates/apartments', url_prefix='/apartments')

# Importiere Routen, nachdem der Blueprint erstellt wurde, um zirkuläre Abhängigkeiten zu vermeiden
from . import routes 
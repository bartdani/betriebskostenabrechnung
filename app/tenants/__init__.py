from flask import Blueprint

# Blueprint für Mieter und Verträge
bp_tenants = Blueprint('tenants', __name__, template_folder='../templates/tenants', url_prefix='/tenants')

# Importiere Routen am Ende, um Zirkelbezüge zu vermeiden
from . import routes 
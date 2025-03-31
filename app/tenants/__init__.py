from flask import Blueprint

# Blueprint für Mieter und Verträge
bp_tenants = Blueprint('tenants', __name__, template_folder='templates')

# Importiere Routen am Ende, um Zirkelbezüge zu vermeiden
from app.tenants import routes 
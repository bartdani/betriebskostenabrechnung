from flask import Blueprint

cost_types_bp = Blueprint('cost_types', __name__, template_folder='../templates/cost_types', url_prefix='/cost-types')

# Importiere Routen am Ende, um Zirkelbezüge zu vermeiden
from . import routes 
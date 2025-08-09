from flask import Blueprint

meters_bp = Blueprint('meters', __name__, template_folder='../templates/meters', url_prefix='/meters')

# Importiere Routen nach der Blueprint-Erstellung
from . import routes  # noqa: E402,F401



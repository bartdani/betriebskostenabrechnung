from flask import Blueprint

billing_bp = Blueprint('billing', __name__, template_folder='../templates/billing', url_prefix='/billing')

# Routen registrieren
from . import routes  # noqa: E402,F401



from flask import Blueprint

contracts_bp = Blueprint('contracts', __name__, template_folder='../templates/contracts', url_prefix='/contracts')

from . import routes  # noqa: E402,F401



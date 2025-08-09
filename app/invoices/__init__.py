from flask import Blueprint

invoices_bp = Blueprint('invoices', __name__, template_folder='../templates/invoices', url_prefix='/invoices')

from . import routes  # noqa: E402,F401



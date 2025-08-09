from flask import Blueprint

warnings_bp = Blueprint('warnings', __name__, template_folder='../templates/warnings', url_prefix='/warnings')

from . import routes  # noqa: E402,F401



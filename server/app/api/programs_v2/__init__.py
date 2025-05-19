from flask import Blueprint

programs_bp = Blueprint('programs', __name__)

from . import list_routes  # noqa: E402, F401
from . import detail_routes  # noqa: E402, F401
from . import crud_routes  # noqa: E402, F401 
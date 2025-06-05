from flask import Blueprint

# Blueprint for beneficiaries endpoints (v2 refactor)
beneficiaries_bp = Blueprint('beneficiaries', __name__)

# Import route modules to register endpoints with blueprint
from . import list_routes  # noqa: E402, F401
from . import detail_routes  # noqa: E402, F401
from . import trainer_routes  # noqa: E402, F401
from . import notes_routes  # noqa: E402, F401
from . import documents_routes  # noqa: E402, F401
from . import evaluations_routes  # noqa: E402, F401 

from app.utils.logging import logger
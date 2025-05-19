from flask import Blueprint

# Blueprint for beneficiaries endpoints (v2 refactor)
beneficiaries_bp = Blueprint('beneficiaries', __name__)

# Import route modules to register endpoints with blueprint
from . import list_routes  # noqa: E402, F401 
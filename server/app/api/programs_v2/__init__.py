from flask import Blueprint

programs_bp = Blueprint('programs_v2', __name__)

from . import list_routes  # noqa: E402, F401
from . import detail_routes  # noqa: E402, F401
from . import crud_routes  # noqa: E402, F401
from . import module_routes  # noqa: E402, F401
from . import progress_routes  # noqa: E402, F401
from . import session_routes  # noqa: E402, F401
from . import enrollment_routes  # noqa: E402, F401
from . import util_routes  # noqa: E402, F401

from app.utils.logging import logger
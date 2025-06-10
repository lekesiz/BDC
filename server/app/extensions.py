"""Extensions module for the Flask application."""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_caching import Cache
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
import logging

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()
cors = CORS()
cache = Cache()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)
socketio = SocketIO()

# Setup logging
logger = logging.getLogger('bdc')

# Redis client placeholder (will be initialized in app factory if configured)
redis_client = None
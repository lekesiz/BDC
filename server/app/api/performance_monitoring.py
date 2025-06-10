"""Performance monitoring API (stub for compatibility)."""

import logging
from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)

# Create blueprint
performance_bp = Blueprint('performance', __name__, url_prefix='/api/performance')


@performance_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Performance monitoring service is running'
    })


def register_performance_monitoring(app):
    """Register performance monitoring API (stub)."""
    logger.info("Performance monitoring API registered (stub)")
    return True
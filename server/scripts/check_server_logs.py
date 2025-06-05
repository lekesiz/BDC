#!/usr/bin/env python
"""Check server error logs."""

from app import create_app
from config import DevelopmentConfig
import logging
import traceback

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

app = create_app(DevelopmentConfig)

# Add a custom error handler to capture all errors
@app.errorhandler(Exception)
def handle_exception(e):
    logger.info(f"=== ERROR CAUGHT ===")
    logger.info(f"Error type: {type(e)}")
    logger.info(f"Error message: {str(e)}")
    logger.info(f"Traceback:")
    traceback.print_exc()
    return {'error': 'server_error', 'message': str(e)}, 500

# Start the app in debug mode
if __name__ == '__main__':
    logger.info("Starting server with debug logging...")
    app.run(debug=True, port=5002)  # Different port to not conflict
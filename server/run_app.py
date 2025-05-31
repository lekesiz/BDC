#!/usr/bin/env python3
"""Run the Flask application with clean architecture initialization."""

import sys
import os
import logging

# Monkey patch eventlet first
import eventlet
eventlet.monkey_patch()

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    try:
        # Import app factory
        from app import create_app
        
        logger.info("Creating Flask application with clean architecture...")
        
        # Create the app using the new clean architecture
        app = create_app()
        
        logger.info("Application created successfully")
        
        # Initialize database and create test data
        _initialize_database(app)
        
        # Run the application
        _run_application(app)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


def _initialize_database(app):
    """Initialize database with test data."""
    try:
        from app.core.database_manager import database_initializer, migration_manager
        
        logger.info("Initializing database...")
        
        with app.app_context():
            # Initialize database with test data
            success = database_initializer.initialize_database(
                app, 
                create_tables=True,
                create_test_data=True
            )
            
            if not success:
                logger.error("Database initialization failed")
                return
            
            # Run migrations
            logger.info("Running database migrations...")
            results = migration_manager.run_all_migrations()
            
            successful = sum(1 for r in results if r.status.value == 'success')
            skipped = sum(1 for r in results if r.status.value == 'skipped')
            failed = sum(1 for r in results if r.status.value == 'failed')
            
            logger.info(f"Migration summary: {successful} successful, {skipped} skipped, {failed} failed")
            
            if failed > 0:
                logger.warning("Some migrations failed, check logs for details")
            
            # Verify admin user
            _verify_admin_user()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def _verify_admin_user():
    """Verify admin user exists and can login."""
    try:
        from app.models.user import User
        
        admin = User.query.filter_by(email='admin@bdc.com').first()
        if admin:
            if admin.verify_password('Admin123!'):
                logger.info("✅ Admin user verified successfully")
            else:
                logger.warning("⚠️  Admin user exists but password verification failed")
            
            # List all users
            users = User.query.all()
            logger.info(f"📊 Total users in database: {len(users)}")
            for user in users:
                logger.info(f"  - {user.email} ({user.role})")
        else:
            logger.warning("⚠️  Admin user not found")
            
    except Exception as e:
        logger.error(f"Admin user verification failed: {e}")


def _run_application(app):
    """Run the Flask application."""
    try:
        logger.info("Starting Flask server with Socket.IO...")
        
        # Get configuration
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5001))
        debug = app.config.get('DEBUG', False)
        
        logger.info(f"🚀 Server starting on http://{host}:{port}")
        logger.info(f"🔧 Debug mode: {'enabled' if debug else 'disabled'}")
        logger.info(f"🌍 Environment: {app.config.get('ENV', 'development')}")
        
        # Import socketio after app creation to avoid import-time dependencies
        from app.extensions import socketio
        
        # Import socketio events to register handlers
        try:
            from app import socketio_events
            from app import socketio_basic
            logger.info("✅ SocketIO event handlers loaded")
        except ImportError as e:
            logger.warning(f"⚠️  Could not load SocketIO handlers: {e}")
        
        # Run the application
        socketio.run(
            app, 
            host=host, 
            port=port, 
            debug=debug,
            use_reloader=False  # Disable reloader to avoid double initialization
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == '__main__':
    main()
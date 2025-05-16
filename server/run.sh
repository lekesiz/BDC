#!/bin/bash

# Initialize the database first
echo "Initializing database..."
python init_db.py

# Start Flask without debug mode to avoid reloader issues  
echo "Starting Flask server..."
export FLASK_ENV=development
export FLASK_APP=app
python -m flask run --host=0.0.0.0 --port=5001 --no-reload
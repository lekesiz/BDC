#!/bin/bash
# Setup script for BDC application development environment

set -e

echo "Setting up BDC development environment..."

# Check for required tools
echo "Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "Error: docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed"
    exit 1
fi

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r server/requirements.txt
pip install -r server/requirements-test.txt

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd client
npm install
cd ..

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p server/uploads
mkdir -p server/logs

# Set up sample .env file
echo "Creating sample .env file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Please edit the .env file with your configuration."
fi

# Setup database
echo "Setting up database..."
cd server
python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
cd ..

echo "Setup complete! You can now run the application:"
echo "- Backend: cd server && flask run"
echo "- Frontend: cd client && npm run dev"
echo "- Docker: docker-compose up"
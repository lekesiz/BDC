#!/bin/bash

# Kill any process on port 9888
echo "Stopping any process on port 9888..."
lsof -ti:9888 | xargs kill -9 2>/dev/null

# Create a temporary modified version of the API that uses port 9888
echo "Starting API server on port 9888..."
sed 's/port=8888/port=9888/' server/complete_test_api.py > server/temp_api.py
python3 server/temp_api.py

# Clean up on exit
trap "rm -f server/temp_api.py" EXIT
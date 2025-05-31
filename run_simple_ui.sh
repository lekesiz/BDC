#!/bin/bash

# Kill any processes using our ports
echo "Stopping any processes on ports 8090 and 9888..."
lsof -ti:8090 | xargs kill -9 2>/dev/null
lsof -ti:9888 | xargs kill -9 2>/dev/null

# Start API server with modified port in background
echo "Starting API server on port 9888..."
sed 's/port=8888/port=9888/' server/complete_test_api.py > server/temp_api.py
python3 server/temp_api.py &
API_PID=$!

# Wait for API server to start
sleep 2

# Start HTTP server for client files in background
echo "Starting HTTP server on port 8090..."
cd client
python3 -m http.server 8090 &
HTTP_PID=$!

# Open browser
echo "Opening enhanced login in browser..."
open http://localhost:8090/enhanced-login.html

echo "Servers are running. Press Ctrl+C to stop."
echo "Enhanced login: http://localhost:8090/enhanced-login.html"
echo "API server: http://localhost:9888/health"

# Function to clean up on exit
cleanup() {
    echo "Shutting down servers..."
    kill $API_PID $HTTP_PID 2>/dev/null
    rm -f server/temp_api.py
    exit 0
}

# Set up cleanup on script termination
trap cleanup INT TERM

# Wait for user to stop the script
wait
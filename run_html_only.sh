#!/bin/bash

# Kill any process on port 8090
echo "Stopping any process on port 8090..."
lsof -ti:8090 | xargs kill -9 2>/dev/null

# Start HTTP server for client files
echo "Starting HTTP server on port 8090..."
cd client
python3 -m http.server 8090
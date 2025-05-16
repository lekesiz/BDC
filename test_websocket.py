#!/usr/bin/env python3
"""Test WebSocket connections."""

import socketio
import time

# Test Socket.IO connection
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to Socket.IO server")

@sio.event
def connect_error(data):
    print(f"Connection error: {data}")

@sio.event
def disconnect():
    print("Disconnected from Socket.IO server")

@sio.on('connected')
def on_connected(data):
    print(f"Received connected event: {data}")

# Try to connect with authentication
token = None
try:
    # First login to get token
    import requests
    login_data = {
        "email": "admin@bdc.com",
        "password": "Admin123!"
    }
    response = requests.post("http://localhost:5001/api/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"Got token: {token[:20]}...")
    else:
        print(f"Login failed: {response.text}")
except Exception as e:
    print(f"Login error: {e}")

if token:
    try:
        print("Attempting Socket.IO connection...")
        sio.connect('http://localhost:5001', 
                   auth={'token': token},
                   transports=['websocket', 'polling'],
                   wait_timeout=10)
        
        # Wait a bit to see events
        time.sleep(2)
        
        # Disconnect
        sio.disconnect()
        
    except Exception as e:
        print(f"Socket.IO connection error: {e}")
else:
    print("No token available, skipping Socket.IO test")
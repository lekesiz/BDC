#!/usr/bin/env python3
"""Final test of all WebSocket and API endpoints."""

import requests
import json
import time
import socketio

# URLs
login_url = "http://localhost:5001/api/auth/login"
notification_url = "http://localhost:5001/api/notifications/unread-count"
me_url = "http://localhost:5001/api/users/me"

print("BDC System Final Test")
print("=====================\n")

# 1. Login Test
print("1. Testing Login...")
login_data = {
    "email": "admin@bdc.com",
    "password": "Admin123!"
}

login_response = requests.post(login_url, json=login_data)
if login_response.status_code == 200:
    token = login_response.json()['access_token']
    print(f"   ✓ Login successful")
    print(f"   Token: {token[:20]}...")
else:
    print(f"   ✗ Login failed: {login_response.text}")
    return

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. Test /me endpoint
print("\n2. Testing /me endpoint...")
me_response = requests.get(me_url, headers=headers)
if me_response.status_code == 200:
    user_data = me_response.json()
    print(f"   ✓ User data retrieved")
    print(f"   User: {user_data.get('email')} ({user_data.get('role')})")
else:
    print(f"   ✗ Failed: {me_response.text}")

# 3. Test notification endpoint
print("\n3. Testing notification endpoint...")
notif_response = requests.get(notification_url, headers=headers)
if notif_response.status_code == 200:
    notif_data = notif_response.json()
    print(f"   ✓ Notification count retrieved")
    print(f"   Unread count: {notif_data.get('unread_count')}")
else:
    print(f"   ✗ Failed: {notif_response.text}")

# 4. Test Socket.IO
print("\n4. Testing Socket.IO connection...")
sio = socketio.Client(logger=True, engineio_logger=True)

connected = False

@sio.event
def connect():
    global connected
    connected = True
    print("   ✓ Connected to Socket.IO")

@sio.event
def connect_error(data):
    print(f"   ✗ Connection error: {data}")

@sio.event
def disconnect():
    print("   Disconnected from Socket.IO")

@sio.on('connected')
def on_connected(data):
    print(f"   Server says: {data}")

try:
    sio.connect('http://localhost:5001', 
               auth={'token': token},
               transports=['polling', 'websocket'],
               wait_timeout=5)
    
    time.sleep(2)
    
    if connected:
        print("   ✓ Socket.IO is working")
    else:
        print("   ✗ Socket.IO connection failed")
    
    sio.disconnect()
    
except Exception as e:
    print(f"   ✗ Socket.IO error: {e}")

print("\n\nSummary")
print("=======")
print("API Login: ✓")
print(f"API /me: {'✓' if me_response.status_code == 200 else '✗'}")
print(f"API notifications: {'✓' if notif_response.status_code == 200 else '✗'}")
print(f"Socket.IO: {'✓' if connected else '✗'}")
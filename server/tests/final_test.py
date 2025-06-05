#!/usr/bin/env python3
"""Final test of all WebSocket and API endpoints."""

import requests
import json
import time
import socketio

from app.utils.logging import logger

# URLs
login_url = "http://localhost:5001/api/auth/login"
notification_url = "http://localhost:5001/api/notifications/unread-count"
me_url = "http://localhost:5001/api/users/me"

logger.info("BDC System Final Test")
logger.info("=====================\n")

# 1. Login Test
logger.info("1. Testing Login...")
login_data = {
    "email": "admin@bdc.com",
    "password": "Admin123!"
}

login_response = requests.post(login_url, json=login_data)
if login_response.status_code == 200:
    token = login_response.json()['access_token']
    logger.info(f"   ✓ Login successful")
    logger.info(f"   Token: {token[:20]}...")
else:
    logger.info(f"   ✗ Login failed: {login_response.text}")
    return

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. Test /me endpoint
logger.info("\n2. Testing /me endpoint...")
me_response = requests.get(me_url, headers=headers)
if me_response.status_code == 200:
    user_data = me_response.json()
    logger.info(f"   ✓ User data retrieved")
    logger.info(f"   User: {user_data.get('email')} ({user_data.get('role')})")
else:
    logger.info(f"   ✗ Failed: {me_response.text}")

# 3. Test notification endpoint
logger.info("\n3. Testing notification endpoint...")
notif_response = requests.get(notification_url, headers=headers)
if notif_response.status_code == 200:
    notif_data = notif_response.json()
    logger.info(f"   ✓ Notification count retrieved")
    logger.info(f"   Unread count: {notif_data.get('unread_count')}")
else:
    logger.info(f"   ✗ Failed: {notif_response.text}")

# 4. Test Socket.IO
logger.info("\n4. Testing Socket.IO connection...")
sio = socketio.Client(logger=True, engineio_logger=True)

connected = False

@sio.event
def connect():
    global connected
    connected = True
    logger.info("   ✓ Connected to Socket.IO")

@sio.event
def connect_error(data):
    logger.info(f"   ✗ Connection error: {data}")

@sio.event
def disconnect():
    logger.info("   Disconnected from Socket.IO")

@sio.on('connected')
def on_connected(data):
    logger.info(f"   Server says: {data}")

try:
    sio.connect('http://localhost:5001', 
               auth={'token': token},
               transports=['polling', 'websocket'],
               wait_timeout=5)
    
    time.sleep(2)
    
    if connected:
        logger.info("   ✓ Socket.IO is working")
    else:
        logger.info("   ✗ Socket.IO connection failed")
    
    sio.disconnect()
    
except Exception as e:
    logger.info(f"   ✗ Socket.IO error: {e}")

logger.info("\n\nSummary")
logger.info("=======")
logger.info("API Login: ✓")
logger.info(f"API /me: {'✓' if me_response.status_code == 200 else '✗'}")
logger.info(f"API notifications: {'✓' if notif_response.status_code == 200 else '✗'}")
logger.info(f"Socket.IO: {'✓' if connected else '✗'}")
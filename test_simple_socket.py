#!/usr/bin/env python3
"""Test simple Socket.IO connection."""

import socketio

sio = socketio.Client(logger=True, engineio_logger=True)

@sio.event
def connect():
    print("Connected!")

@sio.event
def connected(data):
    print(f"Server says: {data}")

@sio.event
def connect_error(data):
    print(f"Connection error: {data}")

@sio.event
def disconnect():
    print("Disconnected!")

try:
    print("Trying to connect to localhost:5002...")
    sio.connect('http://localhost:5002')
    sio.wait()
except Exception as e:
    print(f"Error: {e}")
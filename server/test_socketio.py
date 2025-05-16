#!/usr/bin/env python
"""Test Socket.IO connectivity."""

import socketio

# Create a test client
sio = socketio.Client()

@sio.event
def connect():
    print('Connected!')
    sio.emit('message', 'Hello from test client')

@sio.event
def connected(data):
    print(f'Server response: {data}')

@sio.event
def response(data):
    print(f'Echo response: {data}')

@sio.event
def connect_error(data):
    print(f'Connection failed! Error: {data}')

try:
    print('Attempting to connect to server...')
    sio.connect('http://localhost:5001', wait_timeout=5)
    print('Connected successfully!')
    sio.wait()
except Exception as e:
    print(f'Failed to connect: {e}')

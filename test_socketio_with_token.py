import socketio
import time

# Read the token from file
with open('/tmp/bdc_test_token.txt', 'r') as f:
    token = f.read().strip()

print(f'🔑 Using token: {token[:50]}...')

# Create a Socket.IO client
sio = socketio.Client()

# Connection event handlers
@sio.event
def connect():
    print('✅ Connected to server')

@sio.event
def disconnect():
    print('❌ Disconnected from server')

@sio.event
def connected(data):
    print(f'📡 Server response: {data}')

@sio.event
def connect_error(data):
    print(f'❌ Connection error: {data}')

# Try to connect with the token
try:
    print('🔄 Attempting to connect to Socket.IO server...')
    sio.connect('http://localhost:5001', 
               auth={'token': token},
               transports=['polling', 'websocket'],
               wait_timeout=10)
    
    # Wait a bit to see connection status
    time.sleep(2)
    
    if sio.connected:
        print('✅ Socket.IO connection successful\!')
        # Try to join a room
        sio.emit('join_room', {'room': 'test_room'})
        time.sleep(1)
    else:
        print('❌ Socket.IO connection failed')
        
except Exception as e:
    print(f'❌ Connection exception: {e}')
finally:
    if sio.connected:
        sio.disconnect()

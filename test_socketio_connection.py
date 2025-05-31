import socketio
import time

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

# Get a token first
import requests
response = requests.post('http://localhost:5001/api/auth/login', 
    json={'email': 'admin@bdc.com', 'password': 'Admin123\!', 'remember': False})

if response.status_code == 200:
    token = response.json()['access_token']
    print(f'🔑 Token obtained: {token[:50]}...')
    
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
else:
    print(f'❌ Login failed: {response.status_code} - {response.text}')

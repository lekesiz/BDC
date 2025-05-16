#!/usr/bin/env python3
"""Test Redis connection."""

import redis
import sys

try:
    # Try to connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    # Test connection
    r.ping()
    print("✓ Redis is running and accessible")
    
    # Test basic operations
    r.set('test_key', 'test_value')
    value = r.get('test_key')
    print(f"✓ Basic operations working: {value.decode('utf-8')}")
    
    # Cleanup
    r.delete('test_key')
    
except redis.ConnectionError:
    print("✗ Redis is not running")
    print("Start Redis with: brew services start redis")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
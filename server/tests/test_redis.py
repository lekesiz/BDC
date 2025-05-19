#!/usr/bin/env python3
"""Test Redis connection."""

import pytest
import redis


@pytest.fixture
def redis_client():
    """Create Redis client."""
    return redis.Redis(host='localhost', port=6379, db=0)


def test_redis_connection(redis_client):
    """Test Redis connection is working."""
    redis_client.ping()
    # If ping() doesn't raise an exception, connection is working


def test_redis_basic_operations(redis_client):
    """Test basic Redis operations."""
    # Set a key
    redis_client.set('test_key', 'test_value')
    
    # Get the value
    value = redis_client.get('test_key')
    assert value.decode('utf-8') == 'test_value'
    
    # Cleanup
    redis_client.delete('test_key')
    
    # Verify deletion
    assert redis_client.get('test_key') is None


def test_redis_key_expiration(redis_client):
    """Test Redis key expiration."""
    # Set a key with 1 second expiration
    redis_client.setex('temp_key', 1, 'temp_value')
    
    # Verify key exists
    assert redis_client.exists('temp_key') == 1
    
    # Wait for expiration (using time.sleep in test is not ideal, 
    # but acceptable for testing expiration)
    import time
    time.sleep(2)
    
    # Verify key expired
    assert redis_client.exists('temp_key') == 0
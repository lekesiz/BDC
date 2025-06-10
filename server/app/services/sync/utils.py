"""
Utility Functions for Synchronization System

Common utility functions used across sync components:
- Data serialization and compression
- Checksum and hashing utilities
- Time and timestamp helpers
- Network and connectivity utilities
- Validation helpers
"""

import json
import time
import hashlib
import gzip
import zlib
import uuid
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timezone
import pickle
import base64

logger = logging.getLogger(__name__)


def generate_id() -> str:
    """Generate a unique identifier"""
    return str(uuid.uuid4())


def generate_short_id() -> str:
    """Generate a shorter unique identifier"""
    return str(uuid.uuid4()).replace('-', '')[:16]


def current_timestamp() -> float:
    """Get current timestamp as float"""
    return time.time()


def current_timestamp_ms() -> int:
    """Get current timestamp in milliseconds"""
    return int(time.time() * 1000)


def timestamp_to_datetime(timestamp: float) -> datetime:
    """Convert timestamp to datetime object"""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def datetime_to_timestamp(dt: datetime) -> float:
    """Convert datetime object to timestamp"""
    return dt.timestamp()


def format_timestamp(timestamp: float, format_str: str = "%Y-%m-%d %H:%M:%S UTC") -> str:
    """Format timestamp as string"""
    dt = timestamp_to_datetime(timestamp)
    return dt.strftime(format_str)


def calculate_checksum(data: Any, algorithm: str = "sha256") -> str:
    """Calculate checksum for data"""
    
    if isinstance(data, dict):
        # Sort dictionary for consistent hashing
        data_str = json.dumps(data, sort_keys=True, default=str)
    elif isinstance(data, (list, tuple)):
        data_str = json.dumps(data, default=str)
    elif isinstance(data, str):
        data_str = data
    else:
        data_str = str(data)
        
    data_bytes = data_str.encode('utf-8')
    
    if algorithm == "md5":
        return hashlib.md5(data_bytes).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(data_bytes).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(data_bytes).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(data_bytes).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def compress_data(data: bytes, method: str = "gzip") -> bytes:
    """Compress data using specified method"""
    
    if method == "gzip":
        return gzip.compress(data)
    elif method == "zlib":
        return zlib.compress(data)
    else:
        raise ValueError(f"Unsupported compression method: {method}")


def decompress_data(compressed_data: bytes, method: str = "gzip") -> bytes:
    """Decompress data using specified method"""
    
    if method == "gzip":
        return gzip.decompress(compressed_data)
    elif method == "zlib":
        return zlib.decompress(compressed_data)
    else:
        raise ValueError(f"Unsupported compression method: {method}")


def serialize_object(obj: Any, use_compression: bool = False) -> str:
    """Serialize object to string with optional compression"""
    
    # Serialize to bytes
    data_bytes = pickle.dumps(obj)
    
    # Compress if requested
    if use_compression:
        data_bytes = compress_data(data_bytes)
        
    # Encode to base64 string
    return base64.b64encode(data_bytes).decode('utf-8')


def deserialize_object(serialized_str: str, use_compression: bool = False) -> Any:
    """Deserialize object from string"""
    
    # Decode from base64
    data_bytes = base64.b64decode(serialized_str.encode('utf-8'))
    
    # Decompress if needed
    if use_compression:
        data_bytes = decompress_data(data_bytes)
        
    # Deserialize object
    return pickle.loads(data_bytes)


def estimate_size(obj: Any) -> int:
    """Estimate the size of an object in bytes"""
    
    try:
        if isinstance(obj, dict):
            return len(json.dumps(obj, default=str).encode('utf-8'))
        elif isinstance(obj, str):
            return len(obj.encode('utf-8'))
        elif isinstance(obj, bytes):
            return len(obj)
        else:
            return len(str(obj).encode('utf-8'))
    except Exception:
        return 0


def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
            
    return result


def deep_diff(dict1: Dict[str, Any], dict2: Dict[str, Any], path: str = "") -> List[Dict[str, Any]]:
    """Calculate deep differences between two dictionaries"""
    
    differences = []
    
    # Keys in dict1 but not in dict2
    for key in dict1.keys() - dict2.keys():
        differences.append({
            "type": "removed",
            "path": f"{path}.{key}" if path else key,
            "value": dict1[key]
        })
        
    # Keys in dict2 but not in dict1
    for key in dict2.keys() - dict1.keys():
        differences.append({
            "type": "added",
            "path": f"{path}.{key}" if path else key,
            "value": dict2[key]
        })
        
    # Keys in both dictionaries
    for key in dict1.keys() & dict2.keys():
        current_path = f"{path}.{key}" if path else key
        
        if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            # Recursive diff for nested dictionaries
            nested_diffs = deep_diff(dict1[key], dict2[key], current_path)
            differences.extend(nested_diffs)
        elif dict1[key] != dict2[key]:
            differences.append({
                "type": "modified",
                "path": current_path,
                "old_value": dict1[key],
                "new_value": dict2[key]
            })
            
    return differences


def flatten_dict(d: Dict[str, Any], parent_key: str = "", separator: str = ".") -> Dict[str, Any]:
    """Flatten a nested dictionary"""
    
    items = []
    
    for key, value in d.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, separator).items())
        else:
            items.append((new_key, value))
            
    return dict(items)


def unflatten_dict(d: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
    """Unflatten a dictionary with dot notation keys"""
    
    result = {}
    
    for key, value in d.items():
        keys = key.split(separator)
        current = result
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
            
        current[keys[-1]] = value
        
    return result


def validate_email(email: str) -> bool:
    """Simple email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID string format"""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    return sanitized


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    """Decorator for retrying functions with exponential backoff"""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        break
                        
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}")
                    await asyncio.sleep(delay)
                    
            raise last_exception
            
        return wrapper
    return decorator


async def test_connectivity(host: str = "8.8.8.8", port: int = 53, timeout: float = 5.0) -> bool:
    """Test network connectivity to a host"""
    
    try:
        future = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(future, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


def get_memory_usage() -> Dict[str, int]:
    """Get current memory usage statistics"""
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "rss": memory_info.rss,  # Resident Set Size
        "vms": memory_info.vms,  # Virtual Memory Size
        "percent": process.memory_percent(),
        "available": psutil.virtual_memory().available,
        "total": psutil.virtual_memory().total
    }


def format_bytes(bytes_value: int) -> str:
    """Format bytes value as human readable string"""
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration in seconds as human readable string"""
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"


class CircularBuffer:
    """A simple circular buffer implementation"""
    
    def __init__(self, size: int):
        self.size = size
        self.buffer = [None] * size
        self.index = 0
        self.count = 0
        
    def append(self, item: Any):
        """Add item to buffer"""
        self.buffer[self.index] = item
        self.index = (self.index + 1) % self.size
        self.count = min(self.count + 1, self.size)
        
    def get_all(self) -> List[Any]:
        """Get all items in order"""
        if self.count < self.size:
            return self.buffer[:self.count]
        else:
            return self.buffer[self.index:] + self.buffer[:self.index]
            
    def get_latest(self, n: int) -> List[Any]:
        """Get the latest n items"""
        all_items = self.get_all()
        return all_items[-n:] if n <= len(all_items) else all_items


class RateLimiter:
    """Simple rate limiter using token bucket algorithm"""
    
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        
    def acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens"""
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now
        
        # Add tokens based on elapsed time
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class AsyncLock:
    """Async context manager for locking"""
    
    def __init__(self):
        self._lock = asyncio.Lock()
        
    async def __aenter__(self):
        await self._lock.acquire()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()
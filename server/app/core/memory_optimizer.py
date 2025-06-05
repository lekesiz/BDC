"""
Memory Optimization Module
Provides object pooling, memory leak detection, streaming support, and memory monitoring.
"""

import gc
import sys
import psutil
import threading
import weakref
from typing import Dict, Any, List, Optional, Type, Generator
from collections import deque, defaultdict
from datetime import datetime, timedelta
from functools import wraps
from io import BytesIO
import tracemalloc

from app.utils.logging import logger


class ObjectPool:
    """Generic object pool for memory optimization"""
    
    def __init__(self, factory_func, max_size: int = 100, reset_func=None):
        self.factory_func = factory_func
        self.reset_func = reset_func
        self.max_size = max_size
        self.pool = deque()
        self.lock = threading.Lock()
        self.created_count = 0
        self.reused_count = 0
    
    def acquire(self):
        """Get an object from the pool"""
        with self.lock:
            if self.pool:
                obj = self.pool.popleft()
                self.reused_count += 1
                return obj
            else:
                obj = self.factory_func()
                self.created_count += 1
                return obj
    
    def release(self, obj):
        """Return an object to the pool"""
        if obj is None:
            return
        
        with self.lock:
            if len(self.pool) < self.max_size:
                # Reset object state if reset function provided
                if self.reset_func:
                    try:
                        self.reset_func(obj)
                    except Exception as e:
                        logger.error(f"Object reset failed: {e}")
                        return  # Don't return broken objects to pool
                
                self.pool.append(obj)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        with self.lock:
            return {
                'pool_size': len(self.pool),
                'max_size': self.max_size,
                'created_count': self.created_count,
                'reused_count': self.reused_count,
                'reuse_rate': (self.reused_count / (self.created_count + self.reused_count)) * 100 
                             if (self.created_count + self.reused_count) > 0 else 0
            }


class MemoryMonitor:
    """Monitor application memory usage"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.baseline_memory = None
        self.peak_memory = 0
        self.memory_samples = deque(maxlen=100)
        self.gc_stats = {'collections': 0, 'collected': 0}
        self.weak_refs = weakref.WeakSet()
        
        # Start tracemalloc if not already started
        if not tracemalloc.is_tracing():
            tracemalloc.start()
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        try:
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            # Get Python-specific memory info
            gc_stats = {
                'generation_0': gc.get_count()[0],
                'generation_1': gc.get_count()[1],
                'generation_2': gc.get_count()[2],
                'threshold_0': gc.get_threshold()[0],
                'threshold_1': gc.get_threshold()[1],
                'threshold_2': gc.get_threshold()[2]
            }
            
            current_memory = memory_info.rss
            if current_memory > self.peak_memory:
                self.peak_memory = current_memory
            
            # Store memory sample
            self.memory_samples.append({
                'timestamp': datetime.utcnow(),
                'rss': current_memory,
                'vms': memory_info.vms,
                'percent': memory_percent
            })
            
            return {
                'rss': current_memory,
                'rss_mb': current_memory / 1024 / 1024,
                'vms': memory_info.vms,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': memory_percent,
                'peak_rss': self.peak_memory,
                'peak_rss_mb': self.peak_memory / 1024 / 1024,
                'gc_stats': gc_stats,
                'objects_tracked': len(self.weak_refs) if hasattr(self, 'weak_refs') else 0
            }
        
        except Exception as e:
            logger.error(f"Memory monitoring error: {e}")
            return {}
    
    def set_memory_baseline(self):
        """Set the baseline memory usage"""
        memory_info = self.process.memory_info()
        self.baseline_memory = memory_info.rss
        logger.info(f"Memory baseline set: {self.baseline_memory / 1024 / 1024:.2f} MB")
    
    def get_memory_growth(self) -> Optional[float]:
        """Get memory growth since baseline"""
        if self.baseline_memory is None:
            return None
        
        current_memory = self.process.memory_info().rss
        growth = current_memory - self.baseline_memory
        return growth / 1024 / 1024  # Return in MB
    
    def get_top_memory_allocations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top memory allocations using tracemalloc"""
        if not tracemalloc.is_tracing():
            return []
        
        try:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            
            allocations = []
            for stat in top_stats[:limit]:
                allocations.append({
                    'file': stat.traceback.format()[0] if stat.traceback.format() else 'unknown',
                    'size_mb': stat.size / 1024 / 1024,
                    'count': stat.count
                })
            
            return allocations
        
        except Exception as e:
            logger.error(f"Error getting memory allocations: {e}")
            return []
    
    def track_object(self, obj):
        """Track an object for memory monitoring"""
        if hasattr(self, 'weak_refs'):
            self.weak_refs.add(obj)
    
    def force_garbage_collection(self) -> Dict[str, int]:
        """Force garbage collection and return statistics"""
        before_count = len(gc.get_objects())
        
        # Force collection for all generations
        collected = {
            'generation_0': gc.collect(0),
            'generation_1': gc.collect(1),
            'generation_2': gc.collect(2)
        }
        
        after_count = len(gc.get_objects())
        total_collected = sum(collected.values())
        
        self.gc_stats['collections'] += 1
        self.gc_stats['collected'] += total_collected
        
        logger.info(f"Garbage collection: {total_collected} objects collected, "
                   f"{before_count} -> {after_count} objects")
        
        return {
            **collected,
            'total_collected': total_collected,
            'objects_before': before_count,
            'objects_after': after_count
        }


class StreamingFileHandler:
    """Handle file uploads and downloads with streaming for memory efficiency"""
    
    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size
    
    def stream_upload(self, file_obj, destination_path: str) -> int:
        """Stream file upload to disk"""
        total_bytes = 0
        
        try:
            with open(destination_path, 'wb') as dest_file:
                while True:
                    chunk = file_obj.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    dest_file.write(chunk)
                    total_bytes += len(chunk)
            
            logger.info(f"File streamed to {destination_path}: {total_bytes} bytes")
            return total_bytes
        
        except Exception as e:
            logger.error(f"Streaming upload failed: {e}")
            raise
    
    def stream_download(self, file_path: str) -> Generator[bytes, None, None]:
        """Stream file download from disk"""
        try:
            with open(file_path, 'rb') as file_obj:
                while True:
                    chunk = file_obj.read(self.chunk_size)
                    if not chunk:
                        break
                    yield chunk
        
        except Exception as e:
            logger.error(f"Streaming download failed: {e}")
            raise
    
    def stream_response_generator(self, data_generator) -> Generator[bytes, None, None]:
        """Stream data response in chunks"""
        buffer = BytesIO()
        
        for item in data_generator:
            # Convert item to bytes if needed
            if isinstance(item, str):
                item_bytes = item.encode('utf-8')
            elif isinstance(item, dict):
                import json
                item_bytes = json.dumps(item).encode('utf-8')
            else:
                item_bytes = bytes(item)
            
            buffer.write(item_bytes)
            
            # Yield chunk when buffer is full
            if buffer.tell() >= self.chunk_size:
                buffer.seek(0)
                yield buffer.read()
                buffer = BytesIO()
        
        # Yield remaining data
        if buffer.tell() > 0:
            buffer.seek(0)
            yield buffer.read()


class MemoryLeakDetector:
    """Detect potential memory leaks"""
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.memory_history = deque(maxlen=20)
        self.object_counts = defaultdict(int)
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start memory leak monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Memory leak monitoring started")
    
    def stop_monitoring(self):
        """Stop memory leak monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Memory leak monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        import time
        
        while self.monitoring:
            try:
                self._check_memory_usage()
                self._check_object_counts()
                time.sleep(self.check_interval)
            
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
    
    def _check_memory_usage(self):
        """Check for memory usage trends"""
        process = psutil.Process()
        current_memory = process.memory_info().rss
        
        self.memory_history.append({
            'timestamp': datetime.utcnow(),
            'memory': current_memory
        })
        
        # Check for sustained memory growth
        if len(self.memory_history) >= 10:
            recent_samples = list(self.memory_history)[-10:]
            oldest_memory = recent_samples[0]['memory']
            newest_memory = recent_samples[-1]['memory']
            
            growth_rate = (newest_memory - oldest_memory) / oldest_memory
            
            if growth_rate > 0.2:  # 20% growth
                logger.warning(f"Potential memory leak detected: {growth_rate:.2%} growth over "
                             f"{len(recent_samples)} samples")
    
    def _check_object_counts(self):
        """Check for growing object counts"""
        if not tracemalloc.is_tracing():
            return
        
        # Get current object counts by type
        current_counts = defaultdict(int)
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            current_counts[obj_type] += 1
        
        # Compare with previous counts
        for obj_type, current_count in current_counts.items():
            previous_count = self.object_counts.get(obj_type, 0)
            
            if previous_count > 0:
                growth_rate = (current_count - previous_count) / previous_count
                
                if growth_rate > 0.5 and current_count > 1000:  # 50% growth, significant count
                    logger.warning(f"Object type '{obj_type}' growing rapidly: "
                                 f"{previous_count} -> {current_count} ({growth_rate:.2%})")
        
        self.object_counts.update(current_counts)


class MemoryOptimizer:
    """Main memory optimization coordinator"""
    
    def __init__(self):
        self.monitor = MemoryMonitor()
        self.leak_detector = MemoryLeakDetector()
        self.streaming_handler = StreamingFileHandler()
        self.object_pools = {}
        
        # Common object pools
        self._setup_default_pools()
    
    def _setup_default_pools(self):
        """Set up default object pools for common types"""
        # BytesIO pool for file operations
        self.object_pools['bytesio'] = ObjectPool(
            factory_func=lambda: BytesIO(),
            reset_func=lambda obj: obj.seek(0) or obj.truncate(0),
            max_size=50
        )
        
        # List pool for temporary collections
        self.object_pools['list'] = ObjectPool(
            factory_func=lambda: [],
            reset_func=lambda obj: obj.clear(),
            max_size=100
        )
        
        # Dict pool for temporary dictionaries
        self.object_pools['dict'] = ObjectPool(
            factory_func=lambda: {},
            reset_func=lambda obj: obj.clear(),
            max_size=100
        )
    
    def get_pool(self, pool_name: str) -> Optional[ObjectPool]:
        """Get an object pool by name"""
        return self.object_pools.get(pool_name)
    
    def create_pool(self, name: str, factory_func, reset_func=None, max_size: int = 100) -> ObjectPool:
        """Create a new object pool"""
        pool = ObjectPool(factory_func, max_size, reset_func)
        self.object_pools[name] = pool
        return pool
    
    def start_monitoring(self):
        """Start all memory monitoring"""
        self.monitor.set_memory_baseline()
        self.leak_detector.start_monitoring()
        logger.info("Memory optimization monitoring started")
    
    def stop_monitoring(self):
        """Stop all memory monitoring"""
        self.leak_detector.stop_monitoring()
        logger.info("Memory optimization monitoring stopped")
    
    def get_memory_report(self) -> Dict[str, Any]:
        """Get comprehensive memory report"""
        memory_usage = self.monitor.get_memory_usage()
        memory_growth = self.monitor.get_memory_growth()
        top_allocations = self.monitor.get_top_memory_allocations()
        
        pool_stats = {}
        for name, pool in self.object_pools.items():
            pool_stats[name] = pool.get_stats()
        
        return {
            'memory_usage': memory_usage,
            'memory_growth_mb': memory_growth,
            'top_allocations': top_allocations,
            'object_pools': pool_stats,
            'monitoring_active': self.leak_detector.monitoring
        }
    
    def optimize_memory(self) -> Dict[str, Any]:
        """Perform memory optimization operations"""
        # Force garbage collection
        gc_stats = self.monitor.force_garbage_collection()
        
        # Get memory report
        memory_report = self.get_memory_report()
        
        logger.info("Memory optimization completed")
        
        return {
            'garbage_collection': gc_stats,
            'memory_report': memory_report
        }


# Decorators for memory optimization
def use_object_pool(pool_name: str):
    """Decorator to use object pooling for a function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            pool = memory_optimizer.get_pool(pool_name)
            if not pool:
                return func(*args, **kwargs)
            
            obj = pool.acquire()
            try:
                # Add pooled object to kwargs
                kwargs['_pooled_object'] = obj
                return func(*args, **kwargs)
            finally:
                pool.release(obj)
        
        return wrapper
    return decorator


def memory_efficient(func):
    """Decorator for memory-efficient function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Track memory usage
        memory_optimizer.monitor.track_object(func)
        
        try:
            return func(*args, **kwargs)
        finally:
            # Suggest garbage collection for large operations
            if hasattr(func, '_memory_intensive'):
                gc.collect()
    
    return wrapper


# Global memory optimizer instance
memory_optimizer = MemoryOptimizer()


def init_memory_optimization(app):
    """Initialize memory optimization for Flask app"""
    memory_optimizer.start_monitoring()
    
    # Register cleanup on app teardown
    @app.teardown_appcontext
    def cleanup_memory(exception=None):
        # Force garbage collection periodically
        if memory_optimizer.monitor.get_memory_usage().get('percent', 0) > 80:
            memory_optimizer.monitor.force_garbage_collection()
    
    logger.info("Memory optimization initialized")
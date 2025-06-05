"""
Celery Task Optimization Module
Provides task prioritization, bulk processing, queue management, and resource limiting.
"""

import time
import psutil
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict, deque

from celery import Celery, Task
from celery.signals import task_prerun, task_postrun, task_failure, task_success
from kombu import Queue, Exchange

from app.utils.logging import logger


class PriorityTask(Task):
    """Custom Celery task class with priority support"""
    
    def __init__(self):
        super().__init__()
        self.priority_levels = {
            'critical': 0,   # Highest priority
            'high': 3,
            'normal': 6,     # Default priority
            'low': 9,
            'batch': 12      # Lowest priority (bulk operations)
        }
    
    def apply_async(self, args=None, kwargs=None, priority='normal', **options):
        """Apply task with priority"""
        # Set priority in task options
        options['priority'] = self.priority_levels.get(priority, 6)
        
        return super().apply_async(args, kwargs, **options)


class TaskMetrics:
    """Collect and analyze task execution metrics"""
    
    def __init__(self):
        self.task_stats = defaultdict(lambda: {
            'total_runs': 0,
            'total_time': 0.0,
            'success_count': 0,
            'failure_count': 0,
            'average_time': 0.0,
            'last_run': None,
            'memory_usage': [],
            'recent_times': deque(maxlen=100)
        })
        self.system_stats = {
            'total_tasks': 0,
            'active_tasks': 0,
            'queue_sizes': defaultdict(int),
            'worker_stats': {}
        }
    
    def record_task_start(self, task_name: str, task_id: str):
        """Record task start"""
        self.task_stats[task_name]['last_run'] = datetime.utcnow()
        self.system_stats['active_tasks'] += 1
    
    def record_task_end(self, task_name: str, task_id: str, execution_time: float, 
                       success: bool, memory_used: Optional[float] = None):
        """Record task completion"""
        stats = self.task_stats[task_name]
        
        stats['total_runs'] += 1
        stats['total_time'] += execution_time
        stats['recent_times'].append(execution_time)
        
        if success:
            stats['success_count'] += 1
        else:
            stats['failure_count'] += 1
        
        # Update average time
        stats['average_time'] = stats['total_time'] / stats['total_runs']
        
        # Record memory usage if provided
        if memory_used:
            stats['memory_usage'].append(memory_used)
            if len(stats['memory_usage']) > 50:  # Keep last 50 measurements
                stats['memory_usage'].pop(0)
        
        self.system_stats['active_tasks'] = max(0, self.system_stats['active_tasks'] - 1)
        self.system_stats['total_tasks'] += 1
    
    def get_task_statistics(self, task_name: Optional[str] = None) -> Dict[str, Any]:
        """Get task statistics"""
        if task_name:
            return dict(self.task_stats.get(task_name, {}))
        
        return {
            'system_stats': dict(self.system_stats),
            'task_stats': {name: dict(stats) for name, stats in self.task_stats.items()}
        }
    
    def get_slow_tasks(self, threshold: float = 10.0) -> List[Dict[str, Any]]:
        """Get tasks that are running slower than threshold"""
        slow_tasks = []
        
        for task_name, stats in self.task_stats.items():
            if stats['average_time'] > threshold:
                slow_tasks.append({
                    'task_name': task_name,
                    'average_time': stats['average_time'],
                    'total_runs': stats['total_runs'],
                    'failure_rate': (stats['failure_count'] / stats['total_runs']) * 100 
                                  if stats['total_runs'] > 0 else 0
                })
        
        return sorted(slow_tasks, key=lambda x: x['average_time'], reverse=True)


class QueueManager:
    """Manage Celery queues and routing"""
    
    def __init__(self):
        self.queues = {}
        self.routing_rules = {}
        self.queue_stats = defaultdict(lambda: {
            'pending_tasks': 0,
            'processing_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0
        })
    
    def create_priority_queues(self) -> List[Queue]:
        """Create priority-based queues"""
        queues = [
            Queue('critical', Exchange('priority'), routing_key='critical', 
                  queue_arguments={'x-max-priority': 10}),
            Queue('high', Exchange('priority'), routing_key='high',
                  queue_arguments={'x-max-priority': 10}),
            Queue('normal', Exchange('priority'), routing_key='normal',
                  queue_arguments={'x-max-priority': 10}),
            Queue('low', Exchange('priority'), routing_key='low',
                  queue_arguments={'x-max-priority': 10}),
            Queue('batch', Exchange('batch'), routing_key='batch'),
        ]
        
        for queue in queues:
            self.queues[queue.name] = queue
        
        return queues
    
    def setup_task_routing(self) -> Dict[str, Dict[str, str]]:
        """Setup task routing rules"""
        routing = {
            # Authentication and security tasks
            'app.tasks.auth.*': {'queue': 'critical'},
            'app.tasks.security.*': {'queue': 'critical'},
            
            # Real-time notifications
            'app.tasks.notifications.send_immediate': {'queue': 'high'},
            'app.tasks.realtime.*': {'queue': 'high'},
            
            # User-facing operations
            'app.tasks.evaluations.process': {'queue': 'normal'},
            'app.tasks.appointments.*': {'queue': 'normal'},
            
            # Background processing
            'app.tasks.reports.generate': {'queue': 'low'},
            'app.tasks.analytics.*': {'queue': 'low'},
            
            # Bulk operations
            'app.tasks.bulk.*': {'queue': 'batch'},
            'app.tasks.maintenance.*': {'queue': 'batch'},
            'app.tasks.cleanup.*': {'queue': 'batch'},
        }
        
        self.routing_rules = routing
        return routing
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return dict(self.queue_stats)


class ResourceLimiter:
    """Limit resource usage for Celery tasks"""
    
    def __init__(self, max_memory_mb: int = 1024, max_cpu_percent: float = 80.0):
        self.max_memory_mb = max_memory_mb
        self.max_cpu_percent = max_cpu_percent
        self.current_tasks = {}
    
    def check_resources(self) -> Dict[str, Any]:
        """Check current resource usage"""
        process = psutil.Process()
        
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        cpu_percent = process.cpu_percent()
        
        return {
            'memory_mb': memory_mb,
            'memory_limit_mb': self.max_memory_mb,
            'memory_available': memory_mb < self.max_memory_mb,
            'cpu_percent': cpu_percent,
            'cpu_limit': self.max_cpu_percent,
            'cpu_available': cpu_percent < self.max_cpu_percent,
            'resources_available': memory_mb < self.max_memory_mb and cpu_percent < self.max_cpu_percent
        }
    
    def can_start_task(self, task_name: str) -> bool:
        """Check if resources are available to start a task"""
        resources = self.check_resources()
        return resources['resources_available']
    
    def register_task_start(self, task_id: str, task_name: str):
        """Register task start for resource tracking"""
        self.current_tasks[task_id] = {
            'name': task_name,
            'start_time': datetime.utcnow(),
            'start_memory': psutil.Process().memory_info().rss / 1024 / 1024
        }
    
    def register_task_end(self, task_id: str):
        """Register task end and calculate resource usage"""
        if task_id in self.current_tasks:
            task_info = self.current_tasks.pop(task_id)
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            duration = datetime.utcnow() - task_info['start_time']
            memory_used = end_memory - task_info['start_memory']
            
            return {
                'duration_seconds': duration.total_seconds(),
                'memory_used_mb': memory_used
            }
        
        return None


class BulkTaskProcessor:
    """Process tasks in optimized batches"""
    
    def __init__(self, batch_size: int = 100, max_batch_time: int = 300):
        self.batch_size = batch_size
        self.max_batch_time = max_batch_time
        self.pending_batches = defaultdict(list)
        self.batch_timers = {}
    
    def add_to_batch(self, batch_name: str, task_data: Any, 
                    process_func: Callable, priority: str = 'batch'):
        """Add item to a batch for processing"""
        self.pending_batches[batch_name].append({
            'data': task_data,
            'added_time': datetime.utcnow()
        })
        
        # Check if batch is ready for processing
        if len(self.pending_batches[batch_name]) >= self.batch_size:
            self._process_batch(batch_name, process_func, priority)
        else:
            # Set timer for batch processing
            self._set_batch_timer(batch_name, process_func, priority)
    
    def _process_batch(self, batch_name: str, process_func: Callable, priority: str):
        """Process a complete batch"""
        batch_items = self.pending_batches.pop(batch_name, [])
        if not batch_items:
            return
        
        # Extract data from batch items
        batch_data = [item['data'] for item in batch_items]
        
        # Submit batch processing task
        process_func.apply_async(
            args=[batch_data],
            priority=priority,
            queue='batch'
        )
        
        logger.info(f"Processed batch '{batch_name}' with {len(batch_data)} items")
    
    def _set_batch_timer(self, batch_name: str, process_func: Callable, priority: str):
        """Set timer for batch processing"""
        if batch_name in self.batch_timers:
            return  # Timer already set
        
        def timer_callback():
            self._process_batch(batch_name, process_func, priority)
            self.batch_timers.pop(batch_name, None)
        
        # In a real implementation, use Celery's beat scheduler or Redis for timing
        # For now, just process immediately if batch is old enough
        batch_items = self.pending_batches.get(batch_name, [])
        if batch_items:
            oldest_item = min(batch_items, key=lambda x: x['added_time'])
            age = datetime.utcnow() - oldest_item['added_time']
            
            if age.total_seconds() > self.max_batch_time:
                timer_callback()


class CeleryOptimizer:
    """Main Celery optimization coordinator"""
    
    def __init__(self, celery_app: Optional[Celery] = None):
        self.celery_app = celery_app
        self.metrics = TaskMetrics()
        self.queue_manager = QueueManager()
        self.resource_limiter = ResourceLimiter()
        self.bulk_processor = BulkTaskProcessor()
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup Celery signal handlers for monitoring"""
        
        @task_prerun.connect
        def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
            task_name = sender.name if sender else 'unknown'
            self.metrics.record_task_start(task_name, task_id)
            self.resource_limiter.register_task_start(task_id, task_name)
            
            logger.debug(f"Task starting: {task_name} ({task_id})")
        
        @task_postrun.connect
        def task_postrun_handler(sender=None, task_id=None, task=None, args=None, 
                                kwargs=None, retval=None, state=None, **kwds):
            task_name = sender.name if sender else 'unknown'
            
            # Calculate execution time
            execution_time = getattr(task, '_execution_time', 0.0)
            
            # Get resource usage
            resource_usage = self.resource_limiter.register_task_end(task_id)
            memory_used = resource_usage.get('memory_used_mb') if resource_usage else None
            
            # Record metrics
            success = state == 'SUCCESS'
            self.metrics.record_task_end(task_name, task_id, execution_time, success, memory_used)
            
            logger.debug(f"Task completed: {task_name} ({task_id}) - {state} in {execution_time:.3f}s")
        
        @task_failure.connect
        def task_failure_handler(sender=None, task_id=None, exception=None, einfo=None, **kwds):
            task_name = sender.name if sender else 'unknown'
            logger.error(f"Task failed: {task_name} ({task_id}) - {exception}")
    
    def configure_celery(self, celery_app: Celery) -> Celery:
        """Configure Celery with optimization settings"""
        self.celery_app = celery_app
        
        # Create priority queues
        queues = self.queue_manager.create_priority_queues()
        
        # Setup routing
        routing = self.queue_manager.setup_task_routing()
        
        # Configure Celery
        celery_app.conf.update(
            # Queue configuration
            task_queues=queues,
            task_routes=routing,
            task_default_queue='normal',
            task_default_exchange='priority',
            task_default_exchange_type='direct',
            task_default_routing_key='normal',
            
            # Worker configuration
            worker_prefetch_multiplier=1,  # Disable prefetching for fair distribution
            task_acks_late=True,  # Acknowledge tasks after completion
            worker_disable_rate_limits=False,
            
            # Task execution settings
            task_soft_time_limit=300,  # 5 minutes soft limit
            task_time_limit=600,       # 10 minutes hard limit
            task_reject_on_worker_lost=True,
            
            # Optimization settings
            task_compression='gzip',
            result_compression='gzip',
            task_serializer='json',
            result_serializer='json',
            accept_content=['json'],
            
            # Memory optimization
            worker_max_tasks_per_child=1000,  # Restart workers to prevent memory leaks
            worker_max_memory_per_child=200000,  # 200MB per child
            
            # Monitoring
            task_send_sent_event=True,
            worker_send_task_events=True,
            
            # Beat configuration for periodic tasks
            beat_schedule_filename='celerybeat-schedule',
            beat_sync_every=1,
        )
        
        # Set custom task class
        celery_app.Task = PriorityTask
        
        logger.info("Celery optimization configuration applied")
        return celery_app
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics"""
        task_stats = self.metrics.get_task_statistics()
        queue_stats = self.queue_manager.get_queue_stats()
        resource_stats = self.resource_limiter.check_resources()
        slow_tasks = self.metrics.get_slow_tasks()
        
        return {
            'task_metrics': task_stats,
            'queue_stats': queue_stats,
            'resource_usage': resource_stats,
            'slow_tasks': slow_tasks,
            'optimization_recommendations': self._get_optimization_recommendations(task_stats, slow_tasks)
        }
    
    def _get_optimization_recommendations(self, task_stats: Dict, slow_tasks: List) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Check for slow tasks
        if slow_tasks:
            recommendations.append(f"Consider optimizing {len(slow_tasks)} slow tasks")
        
        # Check task failure rates
        for task_name, stats in task_stats.get('task_stats', {}).items():
            if stats['total_runs'] > 10:
                failure_rate = (stats['failure_count'] / stats['total_runs']) * 100
                if failure_rate > 10:  # More than 10% failure rate
                    recommendations.append(f"High failure rate for task '{task_name}': {failure_rate:.1f}%")
        
        # Check resource usage
        resource_stats = self.resource_limiter.check_resources()
        if resource_stats['memory_mb'] > resource_stats['memory_limit_mb'] * 0.8:
            recommendations.append("Memory usage is high, consider increasing limits or optimizing tasks")
        
        if resource_stats['cpu_percent'] > resource_stats['cpu_limit'] * 0.8:
            recommendations.append("CPU usage is high, consider scaling workers or optimizing tasks")
        
        return recommendations


# Decorators for task optimization
def priority_task(priority: str = 'normal'):
    """Decorator to set task priority"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would be handled by the custom task class
            return func(*args, **kwargs)
        
        wrapper._priority = priority
        return wrapper
    
    return decorator


def batch_task(batch_name: str, batch_size: int = 100):
    """Decorator for batch processing tasks"""
    def decorator(func):
        @wraps(func)
        def wrapper(data_item, **kwargs):
            # Add to batch processor
            celery_optimizer.bulk_processor.add_to_batch(
                batch_name, data_item, func, priority='batch'
            )
        
        return wrapper
    
    return decorator


def resource_limited(max_memory_mb: int = 512, max_cpu_percent: float = 50.0):
    """Decorator to limit task resource usage"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check resources before starting
            if not celery_optimizer.resource_limiter.can_start_task(func.__name__):
                raise Exception(f"Insufficient resources to start task {func.__name__}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Record execution time
                execution_time = time.time() - start_time
                func._execution_time = execution_time
        
        return wrapper
    
    return decorator


# Global optimizer instance
celery_optimizer = CeleryOptimizer()


def init_celery_optimization(celery_app: Celery) -> Celery:
    """Initialize Celery optimization"""
    optimized_celery = celery_optimizer.configure_celery(celery_app)
    logger.info("Celery optimization initialized")
    return optimized_celery
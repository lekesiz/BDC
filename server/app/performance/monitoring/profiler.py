"""
Application Profiler

Advanced profiling tools for identifying performance bottlenecks,
memory leaks, and optimization opportunities.
"""

import cProfile
import pstats
import tracemalloc
import time
import threading
import sys
import gc
import logging
import psutil
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from collections import defaultdict
from contextlib import contextmanager
from functools import wraps
import io


@dataclass
class ProfileResult:
    """Profiling result data"""
    function_name: str
    filename: str
    line_number: int
    call_count: int
    total_time: float
    cumulative_time: float
    per_call_time: float
    percentage: float


@dataclass
class MemorySnapshot:
    """Memory usage snapshot"""
    timestamp: float
    rss_mb: float  # Resident Set Size
    vms_mb: float  # Virtual Memory Size
    shared_mb: float
    text_mb: float
    data_mb: float
    peak_rss_mb: float
    tracemalloc_current_mb: float
    tracemalloc_peak_mb: float


@dataclass
class HotSpot:
    """Performance hotspot identification"""
    location: str
    function_name: str
    total_time: float
    call_count: int
    avg_time_per_call: float
    impact_score: float
    recommendations: List[str]


class Profiler:
    """
    Comprehensive application profiler with multiple profiling strategies.
    """
    
    def __init__(self, enable_memory_tracking: bool = True):
        self.enable_memory_tracking = enable_memory_tracking
        self.profiling_sessions = {}
        self.memory_snapshots = []
        self.function_stats = defaultdict(lambda: {
            'call_count': 0,
            'total_time': 0.0,
            'max_time': 0.0,
            'min_time': float('inf')
        })
        
        # Memory tracking
        if self.enable_memory_tracking:
            tracemalloc.start()
        
        # Profiling state
        self.active_profilers = {}
        self.profile_decorators = {}
        
        # Performance thresholds
        self.slow_function_threshold = 0.1  # 100ms
        self.memory_leak_threshold = 50  # 50MB increase
        
        logging.info("Application profiler initialized")
    
    @contextmanager
    def profile_block(self, name: str):
        """Context manager for profiling code blocks"""
        profiler = cProfile.Profile()
        start_time = time.time()
        
        try:
            profiler.enable()
            yield
        finally:
            profiler.disable()
            end_time = time.time()
            
            # Store profiling results
            self._store_profile_results(name, profiler, end_time - start_time)
    
    def profile_function(self, func_name: Optional[str] = None):
        """Decorator for profiling individual functions"""
        def decorator(func):
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = self._get_memory_usage()
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.time()
                    end_memory = self._get_memory_usage()
                    execution_time = end_time - start_time
                    
                    # Update function statistics
                    self._update_function_stats(name, execution_time)
                    
                    # Log slow functions
                    if execution_time > self.slow_function_threshold:
                        logging.warning(
                            f"Slow function detected: {name} took {execution_time:.3f}s"
                        )
                    
                    # Track memory usage
                    memory_diff = end_memory - start_memory
                    if abs(memory_diff) > 10:  # 10MB threshold
                        logging.info(
                            f"Function {name} memory usage: {memory_diff:+.1f}MB"
                        )
            
            return wrapper
        return decorator
    
    def start_continuous_profiling(self, interval: int = 30):
        """Start continuous profiling in background"""
        def profiling_loop():
            while True:
                try:
                    self._collect_performance_snapshot()
                    time.sleep(interval)
                except Exception as e:
                    logging.error(f"Continuous profiling error: {e}")
                    time.sleep(interval)
        
        thread = threading.Thread(target=profiling_loop, daemon=True)
        thread.start()
        logging.info(f"Continuous profiling started (interval: {interval}s)")
    
    def profile_endpoint(self, endpoint_name: str):
        """Start profiling for a specific endpoint"""
        profiler = cProfile.Profile()
        profiler.enable()
        
        self.active_profilers[endpoint_name] = {
            'profiler': profiler,
            'start_time': time.time(),
            'start_memory': self._get_memory_usage()
        }
        
        return endpoint_name
    
    def stop_endpoint_profiling(self, endpoint_name: str) -> Dict[str, Any]:
        """Stop profiling for endpoint and return results"""
        if endpoint_name not in self.active_profilers:
            return {}
        
        profile_data = self.active_profilers[endpoint_name]
        profiler = profile_data['profiler']
        start_time = profile_data['start_time']
        start_memory = profile_data['start_memory']
        
        # Stop profiling
        profiler.disable()
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        # Analyze results
        results = self._analyze_profile(
            profiler, 
            end_time - start_time,
            end_memory - start_memory
        )
        
        # Clean up
        del self.active_profilers[endpoint_name]
        
        return results
    
    def analyze_memory_usage(self) -> Dict[str, Any]:
        """Analyze current memory usage and detect leaks"""
        if not self.enable_memory_tracking:
            return {'error': 'Memory tracking not enabled'}
        
        # Get current memory stats
        current, peak = tracemalloc.get_traced_memory()
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # Create snapshot
        snapshot = MemorySnapshot(
            timestamp=time.time(),
            rss_mb=memory_info.rss / 1024 / 1024,
            vms_mb=memory_info.vms / 1024 / 1024,
            shared_mb=getattr(memory_info, 'shared', 0) / 1024 / 1024,
            text_mb=getattr(memory_info, 'text', 0) / 1024 / 1024,
            data_mb=getattr(memory_info, 'data', 0) / 1024 / 1024,
            peak_rss_mb=getattr(process.memory_info(), 'peak_wset', memory_info.rss) / 1024 / 1024,
            tracemalloc_current_mb=current / 1024 / 1024,
            tracemalloc_peak_mb=peak / 1024 / 1024
        )
        
        self.memory_snapshots.append(snapshot)
        
        # Keep only recent snapshots
        if len(self.memory_snapshots) > 1000:
            self.memory_snapshots = self.memory_snapshots[-500:]
        
        # Detect memory leaks
        leak_detected = False
        if len(self.memory_snapshots) >= 10:
            recent_growth = (
                self.memory_snapshots[-1].rss_mb - 
                self.memory_snapshots[-10].rss_mb
            )
            if recent_growth > self.memory_leak_threshold:
                leak_detected = True
        
        # Get top memory consumers
        top_consumers = []
        if tracemalloc.is_tracing():
            snapshot_tracemalloc = tracemalloc.take_snapshot()
            top_stats = snapshot_tracemalloc.statistics('lineno')
            
            for stat in top_stats[:10]:
                top_consumers.append({
                    'file': stat.traceback.format()[-1],
                    'size_mb': stat.size / 1024 / 1024,
                    'count': stat.count
                })
        
        return {
            'current_snapshot': snapshot,
            'memory_leak_detected': leak_detected,
            'top_memory_consumers': top_consumers,
            'memory_trend': self._calculate_memory_trend(),
            'gc_stats': self._get_gc_stats()
        }
    
    def identify_hotspots(self, min_impact_score: float = 0.1) -> List[HotSpot]:
        """Identify performance hotspots in the application"""
        hotspots = []
        
        for func_name, stats in self.function_stats.items():
            if stats['call_count'] == 0:
                continue
            
            avg_time = stats['total_time'] / stats['call_count']
            
            # Calculate impact score (frequency * average time)
            impact_score = stats['call_count'] * avg_time
            
            if impact_score >= min_impact_score:
                recommendations = self._generate_hotspot_recommendations(func_name, stats)
                
                hotspot = HotSpot(
                    location=func_name,
                    function_name=func_name.split('.')[-1],
                    total_time=stats['total_time'],
                    call_count=stats['call_count'],
                    avg_time_per_call=avg_time,
                    impact_score=impact_score,
                    recommendations=recommendations
                )
                hotspots.append(hotspot)
        
        # Sort by impact score
        hotspots.sort(key=lambda h: h.impact_score, reverse=True)
        
        return hotspots
    
    def generate_profile_report(self) -> Dict[str, Any]:
        """Generate comprehensive profiling report"""
        # Function statistics
        top_functions = sorted(
            self.function_stats.items(),
            key=lambda x: x[1]['total_time'],
            reverse=True
        )[:20]
        
        # Memory analysis
        memory_analysis = self.analyze_memory_usage()
        
        # Hotspots
        hotspots = self.identify_hotspots()
        
        # System performance
        process = psutil.Process()
        cpu_times = process.cpu_times()
        
        # Generate recommendations
        recommendations = self._generate_performance_recommendations(
            top_functions, memory_analysis, hotspots
        )
        
        return {
            'timestamp': time.time(),
            'profiling_summary': {
                'total_functions_tracked': len(self.function_stats),
                'total_profiling_sessions': len(self.profiling_sessions),
                'memory_snapshots_count': len(self.memory_snapshots)
            },
            'top_functions': [
                {
                    'name': name,
                    'total_time': stats['total_time'],
                    'call_count': stats['call_count'],
                    'avg_time': stats['total_time'] / stats['call_count'],
                    'max_time': stats['max_time'],
                    'min_time': stats['min_time']
                }
                for name, stats in top_functions
            ],
            'memory_analysis': memory_analysis,
            'performance_hotspots': [
                {
                    'location': h.location,
                    'impact_score': h.impact_score,
                    'avg_time_ms': h.avg_time_per_call * 1000,
                    'call_count': h.call_count,
                    'recommendations': h.recommendations
                }
                for h in hotspots[:10]
            ],
            'system_metrics': {
                'cpu_user_time': cpu_times.user,
                'cpu_system_time': cpu_times.system,
                'memory_rss_mb': process.memory_info().rss / 1024 / 1024,
                'memory_vms_mb': process.memory_info().vms / 1024 / 1024,
                'open_files': len(process.open_files()),
                'num_threads': process.num_threads()
            },
            'recommendations': recommendations
        }
    
    def export_profile_data(self, format: str = 'json') -> Union[str, bytes]:
        """Export profiling data in various formats"""
        report = self.generate_profile_report()
        
        if format == 'json':
            import json
            return json.dumps(report, indent=2, default=str)
        elif format == 'csv':
            return self._export_to_csv(report)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    # Private methods
    def _store_profile_results(self, name: str, profiler: cProfile.Profile, total_time: float):
        """Store profiling results for analysis"""
        # Create string buffer to capture profile output
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        stats.print_stats()
        
        self.profiling_sessions[name] = {
            'timestamp': time.time(),
            'total_time': total_time,
            'stats_output': s.getvalue(),
            'profiler': profiler
        }
    
    def _analyze_profile(self, profiler: cProfile.Profile, 
                        execution_time: float, memory_diff: float) -> Dict[str, Any]:
        """Analyze profiling results"""
        # Create stats object
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        # Extract function statistics
        function_stats = []
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            if tt > 0.001:  # Only include functions with meaningful time
                function_stats.append(ProfileResult(
                    function_name=f"{func[2]}",
                    filename=func[0],
                    line_number=func[1],
                    call_count=nc,
                    total_time=tt,
                    cumulative_time=ct,
                    per_call_time=tt / nc if nc > 0 else 0,
                    percentage=(tt / execution_time) * 100 if execution_time > 0 else 0
                ))
        
        # Sort by total time
        function_stats.sort(key=lambda x: x.total_time, reverse=True)
        
        return {
            'execution_time': execution_time,
            'memory_diff_mb': memory_diff,
            'total_function_calls': sum(stat.call_count for stat in function_stats),
            'top_functions': function_stats[:20],
            'bottlenecks': [
                stat for stat in function_stats[:10] 
                if stat.per_call_time > 0.01  # Functions taking >10ms per call
            ]
        }
    
    def _update_function_stats(self, func_name: str, execution_time: float):
        """Update function execution statistics"""
        stats = self.function_stats[func_name]
        stats['call_count'] += 1
        stats['total_time'] += execution_time
        stats['max_time'] = max(stats['max_time'], execution_time)
        stats['min_time'] = min(stats['min_time'], execution_time)
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    def _collect_performance_snapshot(self):
        """Collect a performance snapshot"""
        try:
            # Memory analysis
            memory_analysis = self.analyze_memory_usage()
            
            # Function stats summary
            total_function_time = sum(
                stats['total_time'] for stats in self.function_stats.values()
            )
            
            logging.info(
                f"Performance snapshot - "
                f"Memory: {memory_analysis['current_snapshot'].rss_mb:.1f}MB, "
                f"Function time: {total_function_time:.2f}s, "
                f"Active profilers: {len(self.active_profilers)}"
            )
            
        except Exception as e:
            logging.error(f"Performance snapshot collection failed: {e}")
    
    def _calculate_memory_trend(self) -> Dict[str, float]:
        """Calculate memory usage trend"""
        if len(self.memory_snapshots) < 5:
            return {'trend': 0.0, 'growth_rate': 0.0}
        
        recent_snapshots = self.memory_snapshots[-10:]
        
        # Calculate linear trend
        x_values = list(range(len(recent_snapshots)))
        y_values = [s.rss_mb for s in recent_snapshots]
        
        # Simple linear regression
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        else:
            slope = 0.0
        
        # Growth rate as MB per snapshot
        growth_rate = slope
        
        return {
            'trend': slope,
            'growth_rate': growth_rate,
            'current_memory': recent_snapshots[-1].rss_mb,
            'memory_change_10_snapshots': recent_snapshots[-1].rss_mb - recent_snapshots[0].rss_mb
        }
    
    def _get_gc_stats(self) -> Dict[str, Any]:
        """Get garbage collection statistics"""
        return {
            'gc_counts': gc.get_count(),
            'gc_stats': gc.get_stats(),
            'gc_threshold': gc.get_threshold()
        }
    
    def _generate_hotspot_recommendations(self, func_name: str, stats: Dict) -> List[str]:
        """Generate recommendations for performance hotspots"""
        recommendations = []
        
        avg_time = stats['total_time'] / stats['call_count']
        
        if avg_time > 0.1:  # > 100ms
            recommendations.append("Consider optimizing algorithm or adding caching")
        
        if stats['call_count'] > 1000:
            recommendations.append("High call frequency - consider memoization or batch processing")
        
        if 'database' in func_name.lower() or 'query' in func_name.lower():
            recommendations.append("Database operation detected - consider query optimization or connection pooling")
        
        if 'api' in func_name.lower() or 'request' in func_name.lower():
            recommendations.append("API call detected - consider caching or async processing")
        
        return recommendations
    
    def _generate_performance_recommendations(self, top_functions: List, 
                                            memory_analysis: Dict, 
                                            hotspots: List[HotSpot]) -> List[str]:
        """Generate overall performance recommendations"""
        recommendations = []
        
        # Function-based recommendations
        if top_functions:
            slowest_func = top_functions[0]
            if slowest_func[1]['total_time'] > 5.0:  # > 5 seconds total
                recommendations.append(
                    f"Optimize {slowest_func[0]} - consuming {slowest_func[1]['total_time']:.1f}s total execution time"
                )
        
        # Memory-based recommendations
        if memory_analysis.get('memory_leak_detected'):
            recommendations.append("Memory leak detected - investigate memory usage patterns and ensure proper cleanup")
        
        current_memory = memory_analysis['current_snapshot'].rss_mb
        if current_memory > 1000:  # > 1GB
            recommendations.append(f"High memory usage ({current_memory:.0f}MB) - consider memory optimization")
        
        # Hotspot-based recommendations
        if hotspots:
            top_hotspot = hotspots[0]
            if top_hotspot.impact_score > 1.0:
                recommendations.append(
                    f"Critical hotspot: {top_hotspot.function_name} - impact score {top_hotspot.impact_score:.2f}"
                )
        
        return recommendations
    
    def _export_to_csv(self, report: Dict) -> str:
        """Export report data to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write function statistics
        writer.writerow(['Function', 'Total Time', 'Call Count', 'Avg Time', 'Max Time'])
        for func in report['top_functions']:
            writer.writerow([
                func['name'],
                func['total_time'],
                func['call_count'],
                func['avg_time'],
                func['max_time']
            ])
        
        return output.getvalue()
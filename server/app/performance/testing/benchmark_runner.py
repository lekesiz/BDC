"""
Benchmark Runner

Comprehensive benchmarking system for measuring and comparing performance
across different configurations, versions, and environments.
"""

import time
import psutil
import statistics
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
from pathlib import Path
import subprocess
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor


class BenchmarkType(Enum):
    API_PERFORMANCE = "api_performance"
    DATABASE_PERFORMANCE = "database_performance"
    MEMORY_USAGE = "memory_usage"
    CPU_PERFORMANCE = "cpu_performance"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    CUSTOM = "custom"


class MetricType(Enum):
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    RESOURCE_USAGE = "resource_usage"
    ERROR_RATE = "error_rate"
    SCALABILITY = "scalability"


@dataclass
class BenchmarkConfig:
    """Benchmark configuration"""
    name: str
    benchmark_type: BenchmarkType
    duration_seconds: int = 60
    warmup_seconds: int = 10
    iterations: int = 3
    concurrent_threads: int = 1
    target_function: Optional[Callable] = None
    target_url: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    environment_tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class BenchmarkMetric:
    """Individual benchmark metric"""
    name: str
    value: float
    unit: str
    metric_type: MetricType
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    """Complete benchmark result"""
    config: BenchmarkConfig
    start_time: float
    end_time: float
    duration: float
    iterations_completed: int
    metrics: List[BenchmarkMetric]
    system_metrics: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None


@dataclass
class ComparisonResult:
    """Benchmark comparison result"""
    baseline_result: BenchmarkResult
    comparison_result: BenchmarkResult
    improvements: Dict[str, float]
    regressions: Dict[str, float]
    summary: str


class BenchmarkRunner:
    """
    Advanced benchmarking system with comprehensive performance measurement.
    """
    
    def __init__(self):
        self.results = []
        self.baseline_results = {}
        self.custom_benchmarks = {}
        self.system_monitor = None
        self.monitoring_data = defaultdict(list)
        
        # Performance thresholds
        self.thresholds = {
            'api_response_time': 1000,  # 1 second
            'database_query_time': 100,  # 100ms
            'memory_usage_mb': 512,     # 512MB
            'cpu_usage_percent': 80,    # 80%
        }
        
        logging.info("Benchmark Runner initialized")
    
    def register_custom_benchmark(self, name: str, benchmark_func: Callable, 
                                 config: Dict[str, Any] = None):
        """Register a custom benchmark function"""
        self.custom_benchmarks[name] = {
            'function': benchmark_func,
            'config': config or {}
        }
        logging.info(f"Registered custom benchmark: {name}")
    
    async def run_benchmark(self, config: BenchmarkConfig) -> BenchmarkResult:
        """
        Run a single benchmark with specified configuration.
        """
        logging.info(f"Starting benchmark: {config.name}")
        
        start_time = time.time()
        result = BenchmarkResult(
            config=config,
            start_time=start_time,
            end_time=0,
            duration=0,
            iterations_completed=0,
            metrics=[],
            system_metrics={},
            success=False
        )
        
        try:
            # Start system monitoring
            self._start_system_monitoring()
            
            # Warmup phase
            if config.warmup_seconds > 0:
                logging.info(f"Warmup phase: {config.warmup_seconds} seconds")
                await self._run_warmup(config)
            
            # Run benchmark iterations
            all_metrics = []
            
            for iteration in range(config.iterations):
                logging.info(f"Running iteration {iteration + 1}/{config.iterations}")
                
                iteration_metrics = await self._run_single_iteration(config)
                all_metrics.extend(iteration_metrics)
                result.iterations_completed += 1
            
            # Stop system monitoring and collect data
            self._stop_system_monitoring()
            system_metrics = self._get_system_metrics()
            
            # Aggregate metrics
            aggregated_metrics = self._aggregate_metrics(all_metrics)
            
            # Complete result
            end_time = time.time()
            result.end_time = end_time
            result.duration = end_time - start_time
            result.metrics = aggregated_metrics
            result.system_metrics = system_metrics
            result.success = True
            
            # Store result
            self.results.append(result)
            
            logging.info(f"Benchmark completed: {config.name}")
            return result
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            result.end_time = time.time()
            result.duration = result.end_time - start_time
            
            logging.error(f"Benchmark failed: {config.name} - {e}")
            raise
    
    async def run_benchmark_suite(self, configs: List[BenchmarkConfig]) -> List[BenchmarkResult]:
        """
        Run multiple benchmarks in sequence.
        """
        logging.info(f"Running benchmark suite with {len(configs)} benchmarks")
        results = []
        
        for config in configs:
            try:
                result = await self.run_benchmark(config)
                results.append(result)
                
                # Cool-down period between benchmarks
                await asyncio.sleep(5)
                
            except Exception as e:
                logging.error(f"Benchmark suite error: {e}")
                # Continue with remaining benchmarks
                continue
        
        logging.info(f"Benchmark suite completed: {len(results)}/{len(configs)} successful")
        return results
    
    def run_api_benchmark(self, endpoint_url: str, method: str = 'GET',
                         concurrent_requests: int = 10, 
                         duration_seconds: int = 60) -> BenchmarkResult:
        """
        Run API performance benchmark.
        """
        from .load_tester import LoadTester, LoadTestConfig
        
        config = BenchmarkConfig(
            name=f"API Benchmark - {endpoint_url}",
            benchmark_type=BenchmarkType.API_PERFORMANCE,
            duration_seconds=duration_seconds,
            target_url=endpoint_url,
            parameters={
                'method': method,
                'concurrent_requests': concurrent_requests
            }
        )
        
        # Use load tester for API benchmarking
        load_config = LoadTestConfig(
            base_url=endpoint_url.split('/')[0] + '//' + endpoint_url.split('/')[2],
            endpoints=['/'.join(endpoint_url.split('/')[3:])],
            concurrent_users=concurrent_requests,
            duration_seconds=duration_seconds
        )
        
        load_tester = LoadTester(load_config)
        
        # Run load test synchronously for benchmarking
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            load_result = loop.run_until_complete(
                load_tester.run_load_test("API Benchmark")
            )
            
            # Convert load test result to benchmark result
            return self._convert_load_test_result(config, load_result)
            
        finally:
            loop.close()
    
    def run_database_benchmark(self, query_func: Callable, 
                             iterations: int = 1000) -> BenchmarkResult:
        """
        Run database performance benchmark.
        """
        config = BenchmarkConfig(
            name="Database Benchmark",
            benchmark_type=BenchmarkType.DATABASE_PERFORMANCE,
            iterations=iterations,
            target_function=query_func
        )
        
        start_time = time.time()
        query_times = []
        successful_queries = 0
        
        try:
            for i in range(iterations):
                query_start = time.time()
                
                try:
                    query_func()
                    query_time = time.time() - query_start
                    query_times.append(query_time)
                    successful_queries += 1
                    
                except Exception as e:
                    logging.warning(f"Query {i} failed: {e}")
            
            end_time = time.time()
            
            # Calculate metrics
            metrics = []
            
            if query_times:
                metrics.extend([
                    BenchmarkMetric(
                        name="avg_query_time",
                        value=statistics.mean(query_times) * 1000,  # Convert to ms
                        unit="ms",
                        metric_type=MetricType.LATENCY
                    ),
                    BenchmarkMetric(
                        name="min_query_time",
                        value=min(query_times) * 1000,
                        unit="ms",
                        metric_type=MetricType.LATENCY
                    ),
                    BenchmarkMetric(
                        name="max_query_time",
                        value=max(query_times) * 1000,
                        unit="ms",
                        metric_type=MetricType.LATENCY
                    ),
                    BenchmarkMetric(
                        name="p95_query_time",
                        value=self._percentile(sorted(query_times), 95) * 1000,
                        unit="ms",
                        metric_type=MetricType.LATENCY
                    ),
                    BenchmarkMetric(
                        name="queries_per_second",
                        value=successful_queries / (end_time - start_time),
                        unit="qps",
                        metric_type=MetricType.THROUGHPUT
                    ),
                    BenchmarkMetric(
                        name="success_rate",
                        value=(successful_queries / iterations) * 100,
                        unit="percent",
                        metric_type=MetricType.ERROR_RATE
                    )
                ])
            
            result = BenchmarkResult(
                config=config,
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
                iterations_completed=iterations,
                metrics=metrics,
                system_metrics=self._get_current_system_metrics(),
                success=True
            )
            
            self.results.append(result)
            return result
            
        except Exception as e:
            return BenchmarkResult(
                config=config,
                start_time=start_time,
                end_time=time.time(),
                duration=time.time() - start_time,
                iterations_completed=0,
                metrics=[],
                system_metrics={},
                success=False,
                error_message=str(e)
            )
    
    def run_memory_benchmark(self, memory_intensive_func: Callable,
                           duration_seconds: int = 60) -> BenchmarkResult:
        """
        Run memory usage benchmark.
        """
        config = BenchmarkConfig(
            name="Memory Benchmark",
            benchmark_type=BenchmarkType.MEMORY_USAGE,
            duration_seconds=duration_seconds,
            target_function=memory_intensive_func
        )
        
        start_time = time.time()
        memory_measurements = []
        
        # Start memory monitoring thread
        monitoring_active = threading.Event()
        monitoring_active.set()
        
        def memory_monitor():
            while monitoring_active.is_set():
                memory_info = psutil.virtual_memory()
                process = psutil.Process()
                process_memory = process.memory_info()
                
                measurement = {
                    'timestamp': time.time(),
                    'system_memory_mb': memory_info.used / 1024 / 1024,
                    'system_memory_percent': memory_info.percent,
                    'process_memory_mb': process_memory.rss / 1024 / 1024,
                    'process_memory_vms_mb': process_memory.vms / 1024 / 1024
                }
                memory_measurements.append(measurement)
                time.sleep(0.1)  # Sample every 100ms
        
        monitor_thread = threading.Thread(target=memory_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            # Run memory-intensive function
            end_time = start_time + duration_seconds
            iterations = 0
            
            while time.time() < end_time:
                memory_intensive_func()
                iterations += 1
            
            # Stop monitoring
            monitoring_active.clear()
            monitor_thread.join(timeout=1)
            
            # Analyze memory usage
            if memory_measurements:
                process_memories = [m['process_memory_mb'] for m in memory_measurements]
                system_memories = [m['system_memory_mb'] for m in memory_measurements]
                
                metrics = [
                    BenchmarkMetric(
                        name="peak_process_memory",
                        value=max(process_memories),
                        unit="MB",
                        metric_type=MetricType.RESOURCE_USAGE
                    ),
                    BenchmarkMetric(
                        name="avg_process_memory",
                        value=statistics.mean(process_memories),
                        unit="MB",
                        metric_type=MetricType.RESOURCE_USAGE
                    ),
                    BenchmarkMetric(
                        name="memory_growth",
                        value=max(process_memories) - min(process_memories),
                        unit="MB",
                        metric_type=MetricType.RESOURCE_USAGE
                    ),
                    BenchmarkMetric(
                        name="iterations_completed",
                        value=iterations,
                        unit="count",
                        metric_type=MetricType.THROUGHPUT
                    )
                ]
            else:
                metrics = []
            
            result = BenchmarkResult(
                config=config,
                start_time=start_time,
                end_time=time.time(),
                duration=time.time() - start_time,
                iterations_completed=iterations,
                metrics=metrics,
                system_metrics={'memory_measurements': memory_measurements},
                success=True
            )
            
            self.results.append(result)
            return result
            
        except Exception as e:
            monitoring_active.clear()
            return BenchmarkResult(
                config=config,
                start_time=start_time,
                end_time=time.time(),
                duration=time.time() - start_time,
                iterations_completed=0,
                metrics=[],
                system_metrics={},
                success=False,
                error_message=str(e)
            )
    
    def compare_benchmarks(self, baseline_name: str, 
                          comparison_result: BenchmarkResult) -> ComparisonResult:
        """
        Compare benchmark results against baseline.
        """
        if baseline_name not in self.baseline_results:
            raise ValueError(f"Baseline '{baseline_name}' not found")
        
        baseline_result = self.baseline_results[baseline_name]
        
        # Compare metrics
        improvements = {}
        regressions = {}
        
        baseline_metrics = {m.name: m.value for m in baseline_result.metrics}
        comparison_metrics = {m.name: m.value for m in comparison_result.metrics}
        
        for metric_name in baseline_metrics:
            if metric_name in comparison_metrics:
                baseline_value = baseline_metrics[metric_name]
                comparison_value = comparison_metrics[metric_name]
                
                if baseline_value > 0:
                    change_percent = ((comparison_value - baseline_value) / baseline_value) * 100
                    
                    # Determine if improvement or regression (depends on metric type)
                    if self._is_improvement(metric_name, change_percent):
                        improvements[metric_name] = abs(change_percent)
                    else:
                        regressions[metric_name] = abs(change_percent)
        
        # Generate summary
        summary = self._generate_comparison_summary(improvements, regressions)
        
        return ComparisonResult(
            baseline_result=baseline_result,
            comparison_result=comparison_result,
            improvements=improvements,
            regressions=regressions,
            summary=summary
        )
    
    def set_baseline(self, name: str, result: BenchmarkResult):
        """Set a benchmark result as baseline for future comparisons"""
        self.baseline_results[name] = result
        logging.info(f"Set baseline: {name}")
    
    def generate_report(self, results: List[BenchmarkResult] = None) -> Dict[str, Any]:
        """
        Generate comprehensive benchmark report.
        """
        if results is None:
            results = self.results
        
        report = {
            'timestamp': time.time(),
            'total_benchmarks': len(results),
            'successful_benchmarks': sum(1 for r in results if r.success),
            'failed_benchmarks': sum(1 for r in results if not r.success),
            'benchmarks': []
        }
        
        for result in results:
            benchmark_data = {
                'name': result.config.name,
                'type': result.config.benchmark_type.value,
                'success': result.success,
                'duration': result.duration,
                'iterations': result.iterations_completed,
                'metrics': [asdict(m) for m in result.metrics],
                'system_metrics': result.system_metrics
            }
            
            if not result.success:
                benchmark_data['error'] = result.error_message
            
            report['benchmarks'].append(benchmark_data)
        
        # Add performance summary
        report['performance_summary'] = self._generate_performance_summary(results)
        
        return report
    
    def export_results(self, filename: str, format: str = 'json'):
        """Export benchmark results to file"""
        report = self.generate_report()
        
        if format.lower() == 'json':
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        elif format.lower() == 'csv':
            self._export_to_csv(report, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logging.info(f"Results exported to {filename}")
    
    # Private methods
    
    async def _run_warmup(self, config: BenchmarkConfig):
        """Run warmup phase"""
        if config.target_function:
            # Run function-based warmup
            for _ in range(min(10, config.iterations)):
                config.target_function()
        elif config.target_url:
            # Run URL-based warmup
            import aiohttp
            async with aiohttp.ClientSession() as session:
                for _ in range(5):
                    try:
                        async with session.get(config.target_url) as response:
                            await response.read()
                    except:
                        pass
    
    async def _run_single_iteration(self, config: BenchmarkConfig) -> List[BenchmarkMetric]:
        """Run a single benchmark iteration"""
        if config.benchmark_type == BenchmarkType.CUSTOM:
            return await self._run_custom_benchmark(config)
        elif config.target_function:
            return self._run_function_benchmark(config)
        elif config.target_url:
            return await self._run_url_benchmark(config)
        else:
            raise ValueError("No benchmark target specified")
    
    def _run_function_benchmark(self, config: BenchmarkConfig) -> List[BenchmarkMetric]:
        """Run function-based benchmark"""
        start_time = time.time()
        
        try:
            result = config.target_function()
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000  # Convert to ms
            
            return [
                BenchmarkMetric(
                    name="execution_time",
                    value=execution_time,
                    unit="ms",
                    metric_type=MetricType.LATENCY
                )
            ]
            
        except Exception as e:
            return [
                BenchmarkMetric(
                    name="error_rate",
                    value=100,
                    unit="percent",
                    metric_type=MetricType.ERROR_RATE,
                    tags={'error': str(e)}
                )
            ]
    
    async def _run_url_benchmark(self, config: BenchmarkConfig) -> List[BenchmarkMetric]:
        """Run URL-based benchmark"""
        import aiohttp
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(config.target_url) as response:
                    content = await response.read()
                    end_time = time.time()
                    
                    response_time = (end_time - start_time) * 1000
                    
                    return [
                        BenchmarkMetric(
                            name="response_time",
                            value=response_time,
                            unit="ms",
                            metric_type=MetricType.LATENCY
                        ),
                        BenchmarkMetric(
                            name="response_size",
                            value=len(content),
                            unit="bytes",
                            metric_type=MetricType.THROUGHPUT
                        ),
                        BenchmarkMetric(
                            name="status_code",
                            value=response.status,
                            unit="code",
                            metric_type=MetricType.ERROR_RATE
                        )
                    ]
        except Exception as e:
            return [
                BenchmarkMetric(
                    name="error_rate",
                    value=100,
                    unit="percent",
                    metric_type=MetricType.ERROR_RATE,
                    tags={'error': str(e)}
                )
            ]
    
    async def _run_custom_benchmark(self, config: BenchmarkConfig) -> List[BenchmarkMetric]:
        """Run custom benchmark"""
        if config.name not in self.custom_benchmarks:
            raise ValueError(f"Custom benchmark not found: {config.name}")
        
        benchmark_info = self.custom_benchmarks[config.name]
        benchmark_func = benchmark_info['function']
        
        try:
            result = benchmark_func(**config.parameters)
            
            if isinstance(result, list):
                return result
            elif isinstance(result, BenchmarkMetric):
                return [result]
            else:
                # Convert simple numeric result
                return [
                    BenchmarkMetric(
                        name="custom_metric",
                        value=float(result),
                        unit="units",
                        metric_type=MetricType.THROUGHPUT
                    )
                ]
        except Exception as e:
            return [
                BenchmarkMetric(
                    name="error_rate",
                    value=100,
                    unit="percent",
                    metric_type=MetricType.ERROR_RATE,
                    tags={'error': str(e)}
                )
            ]
    
    def _aggregate_metrics(self, metrics_list: List[List[BenchmarkMetric]]) -> List[BenchmarkMetric]:
        """Aggregate metrics from multiple iterations"""
        if not metrics_list:
            return []
        
        # Group metrics by name
        grouped_metrics = defaultdict(list)
        for metrics in metrics_list:
            for metric in metrics:
                grouped_metrics[metric.name].append(metric.value)
        
        # Calculate aggregated values
        aggregated = []
        for name, values in grouped_metrics.items():
            if values:
                # Find metric type from first metric
                metric_type = MetricType.THROUGHPUT  # Default
                for metrics in metrics_list:
                    for metric in metrics:
                        if metric.name == name:
                            metric_type = metric.metric_type
                            break
                
                aggregated.extend([
                    BenchmarkMetric(
                        name=f"{name}_avg",
                        value=statistics.mean(values),
                        unit="units",
                        metric_type=metric_type
                    ),
                    BenchmarkMetric(
                        name=f"{name}_min",
                        value=min(values),
                        unit="units",
                        metric_type=metric_type
                    ),
                    BenchmarkMetric(
                        name=f"{name}_max",
                        value=max(values),
                        unit="units",
                        metric_type=metric_type
                    )
                ])
                
                if len(values) > 1:
                    aggregated.append(
                        BenchmarkMetric(
                            name=f"{name}_stddev",
                            value=statistics.stdev(values),
                            unit="units",
                            metric_type=metric_type
                        )
                    )
        
        return aggregated
    
    def _start_system_monitoring(self):
        """Start system resource monitoring"""
        self.monitoring_data.clear()
        
        def monitor():
            while self.system_monitor:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                self.monitoring_data['cpu_percent'].append(cpu_percent)
                self.monitoring_data['memory_percent'].append(memory.percent)
                self.monitoring_data['timestamp'].append(time.time())
        
        self.system_monitor = threading.Thread(target=monitor, daemon=True)
        self.system_monitor.start()
    
    def _stop_system_monitoring(self):
        """Stop system resource monitoring"""
        if self.system_monitor:
            self.system_monitor = None
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get aggregated system metrics"""
        if not self.monitoring_data['cpu_percent']:
            return self._get_current_system_metrics()
        
        cpu_values = self.monitoring_data['cpu_percent']
        memory_values = self.monitoring_data['memory_percent']
        
        return {
            'cpu_avg': statistics.mean(cpu_values),
            'cpu_max': max(cpu_values),
            'memory_avg': statistics.mean(memory_values),
            'memory_max': max(memory_values),
            'samples_count': len(cpu_values)
        }
    
    def _get_current_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics snapshot"""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': memory.used / (1024**3),
            'disk_used_percent': disk.percent,
            'disk_free_gb': disk.free / (1024**3)
        }
    
    def _convert_load_test_result(self, config: BenchmarkConfig, 
                                load_result) -> BenchmarkResult:
        """Convert load test result to benchmark result"""
        metrics = [
            BenchmarkMetric(
                name="avg_response_time",
                value=load_result.avg_response_time * 1000,
                unit="ms",
                metric_type=MetricType.LATENCY
            ),
            BenchmarkMetric(
                name="requests_per_second",
                value=load_result.requests_per_second,
                unit="rps",
                metric_type=MetricType.THROUGHPUT
            ),
            BenchmarkMetric(
                name="error_rate",
                value=(load_result.failed_requests / load_result.total_requests) * 100,
                unit="percent",
                metric_type=MetricType.ERROR_RATE
            )
        ]
        
        return BenchmarkResult(
            config=config,
            start_time=load_result.start_time,
            end_time=load_result.end_time,
            duration=load_result.end_time - load_result.start_time,
            iterations_completed=1,
            metrics=metrics,
            system_metrics={},
            success=True
        )
    
    def _percentile(self, sorted_data: List[float], percentile: float) -> float:
        """Calculate percentile from sorted data"""
        if not sorted_data:
            return 0
        
        index = (percentile / 100) * (len(sorted_data) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_data) - 1)
        
        if lower_index == upper_index:
            return sorted_data[lower_index]
        
        weight = index - lower_index
        return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight
    
    def _is_improvement(self, metric_name: str, change_percent: float) -> bool:
        """Determine if metric change is an improvement"""
        # For latency metrics, lower is better
        latency_metrics = ['response_time', 'query_time', 'execution_time']
        if any(keyword in metric_name.lower() for keyword in latency_metrics):
            return change_percent < 0
        
        # For error rate, lower is better
        if 'error' in metric_name.lower():
            return change_percent < 0
        
        # For throughput metrics, higher is better
        throughput_metrics = ['requests_per_second', 'queries_per_second', 'throughput']
        if any(keyword in metric_name.lower() for keyword in throughput_metrics):
            return change_percent > 0
        
        # Default: assume higher is better
        return change_percent > 0
    
    def _generate_comparison_summary(self, improvements: Dict[str, float], 
                                   regressions: Dict[str, float]) -> str:
        """Generate comparison summary text"""
        if not improvements and not regressions:
            return "No significant changes detected"
        
        summary_parts = []
        
        if improvements:
            best_improvement = max(improvements.items(), key=lambda x: x[1])
            summary_parts.append(f"Best improvement: {best_improvement[0]} (+{best_improvement[1]:.1f}%)")
        
        if regressions:
            worst_regression = max(regressions.items(), key=lambda x: x[1])
            summary_parts.append(f"Worst regression: {worst_regression[0]} (-{worst_regression[1]:.1f}%)")
        
        return "; ".join(summary_parts)
    
    def _generate_performance_summary(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Generate performance summary from results"""
        successful_results = [r for r in results if r.success]
        
        if not successful_results:
            return {'status': 'no_successful_benchmarks'}
        
        # Analyze common metrics
        response_times = []
        throughputs = []
        error_rates = []
        
        for result in successful_results:
            for metric in result.metrics:
                if 'response_time' in metric.name or 'execution_time' in metric.name:
                    response_times.append(metric.value)
                elif 'throughput' in metric.name or 'per_second' in metric.name:
                    throughputs.append(metric.value)
                elif 'error' in metric.name:
                    error_rates.append(metric.value)
        
        summary = {
            'total_benchmarks': len(results),
            'successful_benchmarks': len(successful_results),
            'avg_duration': statistics.mean([r.duration for r in successful_results])
        }
        
        if response_times:
            summary['avg_response_time'] = statistics.mean(response_times)
        
        if throughputs:
            summary['avg_throughput'] = statistics.mean(throughputs)
        
        if error_rates:
            summary['avg_error_rate'] = statistics.mean(error_rates)
        
        return summary
    
    def _export_to_csv(self, report: Dict[str, Any], filename: str):
        """Export report to CSV format"""
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Benchmark', 'Type', 'Success', 'Duration', 'Metric', 'Value', 'Unit'])
            
            # Write data
            for benchmark in report['benchmarks']:
                for metric in benchmark['metrics']:
                    writer.writerow([
                        benchmark['name'],
                        benchmark['type'],
                        benchmark['success'],
                        benchmark['duration'],
                        metric['name'],
                        metric['value'],
                        metric['unit']
                    ])
        
        logging.info(f"CSV export completed: {filename}")
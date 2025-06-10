"""
Load Tester

Comprehensive load testing framework for API endpoints and full application testing
with support for various load patterns, realistic user simulation, and detailed reporting.
"""

import asyncio
import aiohttp
import time
import random
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


class LoadPattern(Enum):
    CONSTANT = "constant"
    RAMP_UP = "ramp_up"
    SPIKE = "spike"
    STEP = "step"
    SINE_WAVE = "sine_wave"


class TestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class LoadTestConfig:
    """Load test configuration"""
    base_url: str
    endpoints: List[str]
    concurrent_users: int = 10
    duration_seconds: int = 60
    ramp_up_seconds: int = 10
    pattern: LoadPattern = LoadPattern.CONSTANT
    think_time_min: float = 1.0
    think_time_max: float = 3.0
    timeout_seconds: int = 30
    follow_redirects: bool = True
    verify_ssl: bool = True
    headers: Dict[str, str] = field(default_factory=dict)
    auth_token: Optional[str] = None
    payload_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestScenario:
    """User behavior test scenario"""
    name: str
    steps: List[Dict[str, Any]]
    weight: float = 1.0
    variables: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RequestResult:
    """Individual request result"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    response_size: int
    success: bool
    error_message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class LoadTestResult:
    """Complete load test results"""
    test_name: str
    config: LoadTestConfig
    start_time: float
    end_time: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    errors_by_type: Dict[str, int]
    status_code_distribution: Dict[int, int]
    endpoint_stats: Dict[str, Dict[str, float]]


class LoadTester:
    """
    Advanced load testing framework with realistic user simulation.
    """
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results = []
        self.scenarios = []
        self.status = TestStatus.PENDING
        self.start_time = 0
        self.end_time = 0
        self.active_sessions = 0
        self.session_data = {}
        
        # Statistics tracking
        self.response_times = []
        self.errors = defaultdict(int)
        self.status_codes = defaultdict(int)
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'errors': 0
        })
        
        # Concurrency control
        self.semaphore = asyncio.Semaphore(self.config.concurrent_users)
        self.session = None
        
        logging.info(f"Load tester initialized for {self.config.base_url}")
    
    def add_scenario(self, scenario: TestScenario):
        """Add a user behavior scenario"""
        self.scenarios.append(scenario)
        logging.info(f"Added scenario: {scenario.name}")
    
    async def run_load_test(self, test_name: str = "Load Test") -> LoadTestResult:
        """
        Run the complete load test.
        """
        logging.info(f"Starting load test: {test_name}")
        self.status = TestStatus.RUNNING
        self.start_time = time.time()
        
        try:
            # Initialize HTTP session
            connector = aiohttp.TCPConnector(
                limit=self.config.concurrent_users * 2,
                verify_ssl=self.config.verify_ssl
            )
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.config.headers
            ) as session:
                self.session = session
                
                # Run the load test based on pattern
                await self._execute_load_pattern()
            
            self.end_time = time.time()
            self.status = TestStatus.COMPLETED
            
            # Generate results
            result = self._generate_results(test_name)
            logging.info(f"Load test completed: {test_name}")
            
            return result
            
        except Exception as e:
            self.status = TestStatus.FAILED
            logging.error(f"Load test failed: {e}")
            raise
    
    async def run_stress_test(self, max_users: int = 1000, 
                            step_size: int = 50,
                            step_duration: int = 30) -> List[LoadTestResult]:
        """
        Run stress test with increasing load until failure.
        """
        logging.info(f"Starting stress test up to {max_users} users")
        results = []
        
        current_users = step_size
        while current_users <= max_users:
            # Update config for current step
            step_config = LoadTestConfig(
                base_url=self.config.base_url,
                endpoints=self.config.endpoints,
                concurrent_users=current_users,
                duration_seconds=step_duration,
                pattern=LoadPattern.CONSTANT,
                **{k: v for k, v in self.config.__dict__.items() 
                   if k not in ['concurrent_users', 'duration_seconds', 'pattern']}
            )
            
            # Run step
            step_tester = LoadTester(step_config)
            step_tester.scenarios = self.scenarios.copy()
            
            try:
                result = await step_tester.run_load_test(f"Stress Test - {current_users} users")
                results.append(result)
                
                # Check for failure conditions
                if result.avg_response_time > 5000 or result.failed_requests / result.total_requests > 0.1:
                    logging.warning(f"Performance degradation detected at {current_users} users")
                    break
                    
            except Exception as e:
                logging.error(f"Stress test failed at {current_users} users: {e}")
                break
            
            current_users += step_size
        
        logging.info(f"Stress test completed with {len(results)} steps")
        return results
    
    async def run_spike_test(self, spike_users: int = 500,
                           spike_duration: int = 30,
                           baseline_users: int = 50) -> LoadTestResult:
        """
        Run spike test with sudden load increase.
        """
        logging.info(f"Starting spike test: {baseline_users} -> {spike_users} users")
        
        # This would implement a more complex spike pattern
        # For now, we'll simulate with the spike pattern
        spike_config = LoadTestConfig(
            base_url=self.config.base_url,
            endpoints=self.config.endpoints,
            concurrent_users=spike_users,
            duration_seconds=spike_duration,
            pattern=LoadPattern.SPIKE,
            **{k: v for k, v in self.config.__dict__.items() 
               if k not in ['concurrent_users', 'duration_seconds', 'pattern']}
        )
        
        spike_tester = LoadTester(spike_config)
        spike_tester.scenarios = self.scenarios.copy()
        
        return await spike_tester.run_load_test("Spike Test")
    
    def generate_report(self, results: Union[LoadTestResult, List[LoadTestResult]]) -> str:
        """
        Generate detailed HTML report from test results.
        """
        if isinstance(results, LoadTestResult):
            results = [results]
        
        html_report = self._build_html_report(results)
        
        # Save report to file
        timestamp = int(time.time())
        report_filename = f"load_test_report_{timestamp}.html"
        
        with open(report_filename, 'w') as f:
            f.write(html_report)
        
        logging.info(f"Report generated: {report_filename}")
        return report_filename
    
    # Private methods
    async def _execute_load_pattern(self):
        """Execute load test based on configured pattern"""
        if self.config.pattern == LoadPattern.CONSTANT:
            await self._run_constant_load()
        elif self.config.pattern == LoadPattern.RAMP_UP:
            await self._run_ramp_up_load()
        elif self.config.pattern == LoadPattern.SPIKE:
            await self._run_spike_load()
        elif self.config.pattern == LoadPattern.STEP:
            await self._run_step_load()
        elif self.config.pattern == LoadPattern.SINE_WAVE:
            await self._run_sine_wave_load()
    
    async def _run_constant_load(self):
        """Run constant load pattern"""
        tasks = []
        
        for user_id in range(self.config.concurrent_users):
            task = asyncio.create_task(self._simulate_user(user_id))
            tasks.append(task)
        
        # Wait for all users to complete or timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.config.duration_seconds + 30
            )
        except asyncio.TimeoutError:
            logging.warning("Load test timed out")
            # Cancel remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
    
    async def _run_ramp_up_load(self):
        """Run ramp-up load pattern"""
        ramp_interval = self.config.ramp_up_seconds / self.config.concurrent_users
        tasks = []
        
        for user_id in range(self.config.concurrent_users):
            # Delay start for ramp-up
            await asyncio.sleep(ramp_interval)
            
            task = asyncio.create_task(self._simulate_user(user_id))
            tasks.append(task)
        
        # Wait for remaining duration
        remaining_time = self.config.duration_seconds - self.config.ramp_up_seconds
        if remaining_time > 0:
            await asyncio.sleep(remaining_time)
        
        # Cancel all tasks
        for task in tasks:
            if not task.done():
                task.cancel()
    
    async def _run_spike_load(self):
        """Run spike load pattern"""
        # Start with 10% of users
        initial_users = max(1, self.config.concurrent_users // 10)
        spike_users = self.config.concurrent_users - initial_users
        
        # Start initial users
        initial_tasks = []
        for user_id in range(initial_users):
            task = asyncio.create_task(self._simulate_user(user_id))
            initial_tasks.append(task)
        
        # Wait for spike trigger (1/4 through test)
        spike_trigger_time = self.config.duration_seconds / 4
        await asyncio.sleep(spike_trigger_time)
        
        # Launch spike users
        spike_tasks = []
        for user_id in range(initial_users, self.config.concurrent_users):
            task = asyncio.create_task(self._simulate_user(user_id))
            spike_tasks.append(task)
        
        # Wait for test completion
        remaining_time = self.config.duration_seconds - spike_trigger_time
        await asyncio.sleep(remaining_time)
        
        # Cancel all tasks
        all_tasks = initial_tasks + spike_tasks
        for task in all_tasks:
            if not task.done():
                task.cancel()
    
    async def _run_step_load(self):
        """Run step load pattern"""
        step_duration = self.config.duration_seconds / 4  # 4 steps
        users_per_step = self.config.concurrent_users / 4
        
        tasks = []
        
        for step in range(4):
            # Add users for this step
            start_user = int(step * users_per_step)
            end_user = int((step + 1) * users_per_step)
            
            for user_id in range(start_user, end_user):
                task = asyncio.create_task(self._simulate_user(user_id))
                tasks.append(task)
            
            # Wait for step duration
            if step < 3:  # Don't wait after last step
                await asyncio.sleep(step_duration)
        
        # Wait for final step
        await asyncio.sleep(step_duration)
        
        # Cancel all tasks
        for task in tasks:
            if not task.done():
                task.cancel()
    
    async def _run_sine_wave_load(self):
        """Run sine wave load pattern"""
        import math
        
        base_users = self.config.concurrent_users // 4
        amplitude = self.config.concurrent_users - base_users
        
        tasks = []
        start_time = time.time()
        
        while time.time() - start_time < self.config.duration_seconds:
            # Calculate current user count based on sine wave
            elapsed = time.time() - start_time
            wave_position = (elapsed / self.config.duration_seconds) * 2 * math.pi
            current_users = base_users + int(amplitude * (math.sin(wave_position) + 1) / 2)
            
            # Adjust number of active tasks
            while len([t for t in tasks if not t.done()]) < current_users:
                user_id = len(tasks)
                task = asyncio.create_task(self._simulate_user(user_id))
                tasks.append(task)
            
            await asyncio.sleep(1)  # Check every second
        
        # Cancel remaining tasks
        for task in tasks:
            if not task.done():
                task.cancel()
    
    async def _simulate_user(self, user_id: int):
        """Simulate a single user session"""
        user_start_time = time.time()
        session_data = {'user_id': user_id, 'requests': 0}
        
        try:
            while (time.time() - user_start_time) < self.config.duration_seconds:
                # Choose scenario or endpoint
                if self.scenarios:
                    await self._execute_scenario(user_id, session_data)
                else:
                    await self._execute_random_request(user_id, session_data)
                
                # Think time between requests
                think_time = random.uniform(
                    self.config.think_time_min,
                    self.config.think_time_max
                )
                await asyncio.sleep(think_time)
                
        except asyncio.CancelledError:
            logging.debug(f"User {user_id} cancelled")
        except Exception as e:
            logging.error(f"User {user_id} error: {e}")
    
    async def _execute_scenario(self, user_id: int, session_data: Dict[str, Any]):
        """Execute a test scenario"""
        # Select scenario based on weight
        scenario = self._select_weighted_scenario()
        
        for step in scenario.steps:
            endpoint = step.get('endpoint', random.choice(self.config.endpoints))
            method = step.get('method', 'GET')
            payload = step.get('payload', {})
            
            await self._make_request(endpoint, method, payload, user_id, session_data)
    
    async def _execute_random_request(self, user_id: int, session_data: Dict[str, Any]):
        """Execute a random request to configured endpoints"""
        endpoint = random.choice(self.config.endpoints)
        method = 'GET'  # Default to GET for random requests
        
        await self._make_request(endpoint, method, {}, user_id, session_data)
    
    async def _make_request(self, endpoint: str, method: str, payload: Dict[str, Any],
                          user_id: int, session_data: Dict[str, Any]):
        """Make HTTP request and record results"""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        headers = self.config.headers.copy()
        if self.config.auth_token:
            headers['Authorization'] = f"Bearer {self.config.auth_token}"
        
        request_start = time.time()
        
        try:
            async with self.semaphore:
                if method.upper() == 'GET':
                    async with self.session.get(url, headers=headers) as response:
                        content = await response.read()
                        result = self._create_request_result(
                            endpoint, method, response, content, request_start
                        )
                elif method.upper() == 'POST':
                    async with self.session.post(url, json=payload, headers=headers) as response:
                        content = await response.read()
                        result = self._create_request_result(
                            endpoint, method, response, content, request_start
                        )
                else:
                    # Handle other HTTP methods
                    async with self.session.request(method, url, json=payload, headers=headers) as response:
                        content = await response.read()
                        result = self._create_request_result(
                            endpoint, method, response, content, request_start
                        )
            
            self._record_result(result)
            session_data['requests'] += 1
            
        except Exception as e:
            response_time = time.time() - request_start
            result = RequestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                response_size=0,
                success=False,
                error_message=str(e)
            )
            self._record_result(result)
    
    def _create_request_result(self, endpoint: str, method: str, 
                             response, content: bytes, request_start: float) -> RequestResult:
        """Create request result from response"""
        response_time = time.time() - request_start
        
        return RequestResult(
            endpoint=endpoint,
            method=method,
            status_code=response.status,
            response_time=response_time,
            response_size=len(content),
            success=200 <= response.status < 400,
            error_message=None if 200 <= response.status < 400 else f"HTTP {response.status}"
        )
    
    def _record_result(self, result: RequestResult):
        """Record request result for analysis"""
        self.results.append(result)
        self.response_times.append(result.response_time)
        self.status_codes[result.status_code] += 1
        
        if not result.success:
            error_key = result.error_message or f"HTTP {result.status_code}"
            self.errors[error_key] += 1
        
        # Update endpoint statistics
        endpoint_stat = self.endpoint_stats[result.endpoint]
        endpoint_stat['count'] += 1
        endpoint_stat['total_time'] += result.response_time
        
        if not result.success:
            endpoint_stat['errors'] += 1
    
    def _select_weighted_scenario(self) -> TestScenario:
        """Select scenario based on weight"""
        if not self.scenarios:
            raise ValueError("No scenarios available")
        
        total_weight = sum(s.weight for s in self.scenarios)
        random_value = random.uniform(0, total_weight)
        
        current_weight = 0
        for scenario in self.scenarios:
            current_weight += scenario.weight
            if random_value <= current_weight:
                return scenario
        
        return self.scenarios[-1]  # Fallback
    
    def _generate_results(self, test_name: str) -> LoadTestResult:
        """Generate comprehensive test results"""
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        failed_requests = total_requests - successful_requests
        
        if self.response_times:
            avg_response_time = statistics.mean(self.response_times)
            min_response_time = min(self.response_times)
            max_response_time = max(self.response_times)
            
            sorted_times = sorted(self.response_times)
            p50_response_time = self._percentile(sorted_times, 50)
            p95_response_time = self._percentile(sorted_times, 95)
            p99_response_time = self._percentile(sorted_times, 99)
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p50_response_time = p95_response_time = p99_response_time = 0
        
        duration = self.end_time - self.start_time
        requests_per_second = total_requests / duration if duration > 0 else 0
        
        # Calculate endpoint statistics
        endpoint_stats = {}
        for endpoint, stats in self.endpoint_stats.items():
            if stats['count'] > 0:
                endpoint_stats[endpoint] = {
                    'count': stats['count'],
                    'avg_response_time': stats['total_time'] / stats['count'],
                    'error_rate': (stats['errors'] / stats['count']) * 100
                }
        
        return LoadTestResult(
            test_name=test_name,
            config=self.config,
            start_time=self.start_time,
            end_time=self.end_time,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p50_response_time=p50_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            errors_by_type=dict(self.errors),
            status_code_distribution=dict(self.status_codes),
            endpoint_stats=endpoint_stats
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
        
        # Linear interpolation
        weight = index - lower_index
        return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight
    
    def _build_html_report(self, results: List[LoadTestResult]) -> str:
        """Build HTML report from results"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Load Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .summary { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                .metric { display: inline-block; margin: 10px 20px; }
                .metric-value { font-size: 24px; font-weight: bold; color: #2196F3; }
                .metric-label { font-size: 14px; color: #666; }
                table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .success { color: #4CAF50; }
                .error { color: #f44336; }
            </style>
        </head>
        <body>
            <h1>Load Test Report</h1>
        """
        
        for result in results:
            html += f"""
            <div class="summary">
                <h2>{result.test_name}</h2>
                <div class="metric">
                    <div class="metric-value">{result.total_requests}</div>
                    <div class="metric-label">Total Requests</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{result.requests_per_second:.1f}</div>
                    <div class="metric-label">Requests/sec</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{result.avg_response_time:.0f}ms</div>
                    <div class="metric-label">Avg Response Time</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{(result.failed_requests/result.total_requests*100):.1f}%</div>
                    <div class="metric-label">Error Rate</div>
                </div>
            </div>
            """
        
        html += "</body></html>"
        return html
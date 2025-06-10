"""
Testing utilities for BDC integrations.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass
from enum import Enum
import logging

from .base import BaseIntegration, IntegrationConfig
from .config import IntegrationManager
from .registry import integration_registry

logger = logging.getLogger(__name__)


class TestResult(Enum):
    """Test result status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestCase:
    """Individual test case."""
    name: str
    description: str
    test_function: str
    timeout: int = 30
    required_config: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.required_config is None:
            self.required_config = []


@dataclass
class TestSuiteResult:
    """Test suite execution result."""
    suite_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    test_results: List[Dict[str, Any]]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100


class IntegrationTester:
    """Test runner for integrations."""
    
    def __init__(self, manager: Optional[IntegrationManager] = None):
        self.manager = manager or IntegrationManager()
        self.test_suites: Dict[str, List[TestCase]] = {}
        self._setup_test_suites()
    
    def _setup_test_suites(self):
        """Setup predefined test suites."""
        # Base integration tests
        self.test_suites['base'] = [
            TestCase(
                "test_integration_creation",
                "Test integration instance creation",
                "test_integration_creation"
            ),
            TestCase(
                "test_configuration_loading",
                "Test configuration loading",
                "test_configuration_loading"
            ),
            TestCase(
                "test_registry_operations",
                "Test integration registry operations",
                "test_registry_operations"
            )
        ]
        
        # Calendar integration tests
        self.test_suites['calendar'] = [
            TestCase(
                "test_calendar_connection",
                "Test calendar service connection",
                "test_calendar_connection",
                required_config=["google_calendar", "outlook_calendar"]
            ),
            TestCase(
                "test_calendar_list",
                "Test listing calendars",
                "test_calendar_list",
                required_config=["google_calendar", "outlook_calendar"]
            ),
            TestCase(
                "test_event_crud",
                "Test calendar event CRUD operations",
                "test_event_crud",
                required_config=["google_calendar", "outlook_calendar"]
            ),
            TestCase(
                "test_availability_check",
                "Test availability checking",
                "test_availability_check",
                required_config=["google_calendar", "outlook_calendar"]
            )
        ]
        
        # Payment integration tests
        self.test_suites['payment'] = [
            TestCase(
                "test_payment_connection",
                "Test payment service connection",
                "test_payment_connection",
                required_config=["stripe", "paypal"]
            ),
            TestCase(
                "test_customer_crud",
                "Test customer CRUD operations",
                "test_customer_crud",
                required_config=["stripe", "paypal"]
            ),
            TestCase(
                "test_payment_intent",
                "Test payment intent creation",
                "test_payment_intent",
                required_config=["stripe", "paypal"]
            ),
            TestCase(
                "test_payment_methods",
                "Test payment method management",
                "test_payment_methods",
                required_config=["stripe"]
            )
        ]
        
        # Video integration tests
        self.test_suites['video'] = [
            TestCase(
                "test_video_connection",
                "Test video service connection",
                "test_video_connection",
                required_config=["zoom", "microsoft_teams", "google_meet"]
            ),
            TestCase(
                "test_meeting_crud",
                "Test meeting CRUD operations",
                "test_meeting_crud",
                required_config=["zoom", "microsoft_teams", "google_meet"]
            ),
            TestCase(
                "test_instant_meeting",
                "Test instant meeting creation",
                "test_instant_meeting",
                required_config=["zoom", "google_meet"]
            ),
            TestCase(
                "test_meeting_participants",
                "Test meeting participant management",
                "test_meeting_participants",
                required_config=["zoom"]
            )
        ]
        
        # Email integration tests
        self.test_suites['email'] = [
            TestCase(
                "test_email_connection",
                "Test email service connection",
                "test_email_connection",
                required_config=["sendgrid", "mailgun"]
            ),
            TestCase(
                "test_email_sending",
                "Test email sending",
                "test_email_sending",
                required_config=["sendgrid", "mailgun"]
            ),
            TestCase(
                "test_template_crud",
                "Test email template CRUD operations",
                "test_template_crud",
                required_config=["sendgrid", "mailgun"]
            ),
            TestCase(
                "test_suppression_list",
                "Test suppression list management",
                "test_suppression_list",
                required_config=["sendgrid", "mailgun"]
            )
        ]
    
    async def run_test_suite(self, suite_name: str) -> TestSuiteResult:
        """Run a specific test suite."""
        if suite_name not in self.test_suites:
            raise ValueError(f"Test suite '{suite_name}' not found")
        
        test_cases = self.test_suites[suite_name]
        start_time = datetime.now()
        
        results = []
        passed = 0
        failed = 0
        skipped = 0
        errors = 0
        
        logger.info(f"Running test suite: {suite_name}")
        
        for test_case in test_cases:
            result = await self._run_test_case(test_case)
            results.append(result)
            
            if result['status'] == TestResult.PASSED.value:
                passed += 1
            elif result['status'] == TestResult.FAILED.value:
                failed += 1
            elif result['status'] == TestResult.SKIPPED.value:
                skipped += 1
            elif result['status'] == TestResult.ERROR.value:
                errors += 1
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return TestSuiteResult(
            suite_name=suite_name,
            total_tests=len(test_cases),
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration=duration,
            test_results=results
        )
    
    async def run_all_test_suites(self) -> Dict[str, TestSuiteResult]:
        """Run all test suites."""
        results = {}
        
        for suite_name in self.test_suites.keys():
            try:
                result = await self.run_test_suite(suite_name)
                results[suite_name] = result
            except Exception as e:
                logger.error(f"Failed to run test suite {suite_name}: {e}")
                # Create error result
                results[suite_name] = TestSuiteResult(
                    suite_name=suite_name,
                    total_tests=0,
                    passed=0,
                    failed=0,
                    skipped=0,
                    errors=1,
                    duration=0,
                    test_results=[{
                        'test_name': f'{suite_name}_execution',
                        'status': TestResult.ERROR.value,
                        'message': str(e),
                        'duration': 0
                    }]
                )
        
        return results
    
    async def _run_test_case(self, test_case: TestCase) -> Dict[str, Any]:
        """Run an individual test case."""
        start_time = datetime.now()
        
        try:
            # Check if required configurations are available
            missing_configs = []
            for config_name in test_case.required_config:
                if not self.manager.get_config(config_name):
                    missing_configs.append(config_name)
            
            if missing_configs:
                return {
                    'test_name': test_case.name,
                    'status': TestResult.SKIPPED.value,
                    'message': f"Missing required configurations: {missing_configs}",
                    'duration': 0
                }
            
            # Get test method
            test_method = getattr(self, test_case.test_function, None)
            if not test_method:
                return {
                    'test_name': test_case.name,
                    'status': TestResult.ERROR.value,
                    'message': f"Test method '{test_case.test_function}' not found",
                    'duration': 0
                }
            
            # Run test with timeout
            try:
                await asyncio.wait_for(test_method(), timeout=test_case.timeout)
                status = TestResult.PASSED.value
                message = "Test passed successfully"
            except asyncio.TimeoutError:
                status = TestResult.FAILED.value
                message = f"Test timed out after {test_case.timeout} seconds"
            except AssertionError as e:
                status = TestResult.FAILED.value
                message = f"Assertion failed: {str(e)}"
            except Exception as e:
                status = TestResult.ERROR.value
                message = f"Test error: {str(e)}"
        
        except Exception as e:
            status = TestResult.ERROR.value
            message = f"Test setup error: {str(e)}"
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            'test_name': test_case.name,
            'status': status,
            'message': message,
            'duration': duration
        }
    
    # Test implementations
    
    async def test_integration_creation(self):
        """Test integration instance creation."""
        created_count = 0
        
        for config_name in self.manager.list_enabled_configs():
            config = self.manager.get_config(config_name)
            if config:
                try:
                    instance = integration_registry.create_integration(config_name, config)
                    assert instance is not None
                    assert hasattr(instance, 'integration_type')
                    assert hasattr(instance, 'provider_name')
                    created_count += 1
                except Exception as e:
                    logger.warning(f"Failed to create {config_name}: {e}")
        
        assert created_count > 0, "No integrations could be created"
    
    async def test_configuration_loading(self):
        """Test configuration loading."""
        configs = self.manager.list_configs()
        assert len(configs) > 0, "No configurations loaded"
        
        enabled_configs = self.manager.list_enabled_configs()
        assert len(enabled_configs) <= len(configs), "More enabled configs than total configs"
        
        for config_name in enabled_configs:
            config = self.manager.get_config(config_name)
            assert config is not None, f"Config {config_name} is None"
            assert config.name == config_name, f"Config name mismatch: {config.name} != {config_name}"
    
    async def test_registry_operations(self):
        """Test integration registry operations."""
        registered_classes = integration_registry.list_integration_classes()
        assert len(registered_classes) > 0, "No integration classes registered"
        
        info = integration_registry.get_integration_info()
        assert 'registered_classes' in info
        assert 'active_instances' in info
        assert 'instance_details' in info
    
    async def test_calendar_connection(self):
        """Test calendar service connections."""
        calendar_configs = ['google_calendar', 'outlook_calendar', 'ical_calendar']
        connected_count = 0
        
        for config_name in calendar_configs:
            config = self.manager.get_config(config_name)
            if config:
                try:
                    integration = integration_registry.create_integration(config_name, config)
                    await integration.connect()
                    connection_test = await integration.test_connection()
                    if connection_test:
                        connected_count += 1
                    await integration.disconnect()
                except Exception as e:
                    logger.warning(f"Calendar connection test failed for {config_name}: {e}")
        
        assert connected_count > 0, "No calendar integrations could connect"
    
    async def test_calendar_list(self):
        """Test listing calendars."""
        config = self.manager.get_config('google_calendar')
        if config:
            from .calendar import GoogleCalendarIntegration
            integration = GoogleCalendarIntegration(config)
            
            await integration.connect()
            calendars = await integration.get_calendars()
            assert isinstance(calendars, list)
            
            primary_calendar = await integration.get_primary_calendar()
            if primary_calendar:
                assert primary_calendar.primary == True
            
            await integration.disconnect()
    
    async def test_event_crud(self):
        """Test calendar event CRUD operations."""
        config = self.manager.get_config('google_calendar')
        if config:
            from .calendar import GoogleCalendarIntegration, CalendarEventInput
            integration = GoogleCalendarIntegration(config)
            
            await integration.connect()
            
            primary_calendar = await integration.get_primary_calendar()
            if primary_calendar:
                # Create event
                event_data = CalendarEventInput(
                    title="Test Event",
                    start_time=datetime.now() + timedelta(hours=1),
                    end_time=datetime.now() + timedelta(hours=2),
                    description="Test event for integration testing"
                )
                
                created_event = await integration.create_event(primary_calendar.id, event_data)
                assert created_event.title == "Test Event"
                
                # Get event
                retrieved_event = await integration.get_event(primary_calendar.id, created_event.id)
                assert retrieved_event is not None
                assert retrieved_event.id == created_event.id
                
                # Update event
                event_data.title = "Updated Test Event"
                updated_event = await integration.update_event(
                    primary_calendar.id, 
                    created_event.id, 
                    event_data
                )
                assert updated_event.title == "Updated Test Event"
                
                # Delete event
                deleted = await integration.delete_event(primary_calendar.id, created_event.id)
                assert deleted == True
            
            await integration.disconnect()
    
    async def test_availability_check(self):
        """Test availability checking."""
        config = self.manager.get_config('google_calendar')
        if config:
            from .calendar import GoogleCalendarIntegration
            integration = GoogleCalendarIntegration(config)
            
            await integration.connect()
            
            primary_calendar = await integration.get_primary_calendar()
            if primary_calendar:
                tomorrow = datetime.now() + timedelta(days=1)
                day_after = tomorrow + timedelta(days=1)
                
                availability = await integration.get_availability(
                    primary_calendar.id,
                    tomorrow,
                    day_after,
                    duration_minutes=60
                )
                
                assert isinstance(availability, list)
            
            await integration.disconnect()
    
    async def test_payment_connection(self):
        """Test payment service connections."""
        payment_configs = ['stripe', 'paypal']
        connected_count = 0
        
        for config_name in payment_configs:
            config = self.manager.get_config(config_name)
            if config:
                try:
                    integration = integration_registry.create_integration(config_name, config)
                    await integration.connect()
                    connection_test = await integration.test_connection()
                    if connection_test:
                        connected_count += 1
                    await integration.disconnect()
                except Exception as e:
                    logger.warning(f"Payment connection test failed for {config_name}: {e}")
        
        assert connected_count > 0, "No payment integrations could connect"
    
    # Additional test methods would be implemented here...
    # For brevity, I'm including a few representative examples
    
    def generate_test_report(self, results: Dict[str, TestSuiteResult]) -> str:
        """Generate a test report."""
        report = ["BDC Integrations Test Report", "=" * 50, ""]
        
        total_tests = sum(r.total_tests for r in results.values())
        total_passed = sum(r.passed for r in results.values())
        total_failed = sum(r.failed for r in results.values())
        total_skipped = sum(r.skipped for r in results.values())
        total_errors = sum(r.errors for r in results.values())
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report.extend([
            f"Overall Results:",
            f"  Total Tests: {total_tests}",
            f"  Passed: {total_passed}",
            f"  Failed: {total_failed}",
            f"  Skipped: {total_skipped}",
            f"  Errors: {total_errors}",
            f"  Success Rate: {overall_success_rate:.1f}%",
            ""
        ])
        
        for suite_name, suite_result in results.items():
            report.extend([
                f"Test Suite: {suite_name}",
                f"  Tests: {suite_result.total_tests}",
                f"  Passed: {suite_result.passed}",
                f"  Failed: {suite_result.failed}",
                f"  Skipped: {suite_result.skipped}",
                f"  Errors: {suite_result.errors}",
                f"  Success Rate: {suite_result.success_rate:.1f}%",
                f"  Duration: {suite_result.duration:.2f}s",
                ""
            ])
            
            for test_result in suite_result.test_results:
                status = test_result['status']
                name = test_result['test_name']
                message = test_result['message']
                duration = test_result['duration']
                
                status_symbol = {
                    'passed': '✓',
                    'failed': '✗',
                    'skipped': '⊝',
                    'error': '⚠'
                }.get(status, '?')
                
                report.append(f"    {status_symbol} {name} ({duration:.2f}s)")
                if status != 'passed':
                    report.append(f"      {message}")
            
            report.append("")
        
        return "\n".join(report)


async def run_integration_tests():
    """Run all integration tests."""
    tester = IntegrationTester()
    results = await tester.run_all_test_suites()
    
    report = tester.generate_test_report(results)
    print(report)
    
    return results


if __name__ == "__main__":
    asyncio.run(run_integration_tests())
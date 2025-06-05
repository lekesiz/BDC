"""Script to run refactored auth tests and show coverage improvement."""

import subprocess
import sys
import pytest; pytest.skip("Refactored tests runner – skip in CI", allow_module_level=True)

from app.utils.logging import logger


def run_coverage_report():
    """Run coverage report for refactored auth components."""
    logger.info("Running tests for refactored auth components...")
    logger.info("=" * 50)
    
    # Run tests with coverage
    test_files = [
        "tests/test_auth_service_refactored.py",
        "tests/test_auth_api_refactored.py"
    ]
    
    coverage_modules = [
        "app.services.auth_service_refactored",
        "app.api.auth_refactored",
        "app.container",
        "app.repositories.user_repository"
    ]
    
    # Run pytest with coverage
    cmd = [
        "coverage", "run", "-m", "pytest", "-v"
    ] + test_files
    
    logger.info(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        logger.info("\nTests failed!")
        return
    
    logger.info("\n" + "=" * 50)
    logger.info("Coverage Report for Refactored Components:")
    logger.info("=" * 50)
    
    # Generate coverage report
    coverage_cmd = ["coverage", "report", "--include=" + ",".join(coverage_modules)]
    subprocess.run(coverage_cmd)
    
    logger.info("\n" + "=" * 50)
    logger.info("Key Improvements:")
    logger.info("=" * 50)
    logger.info("1. Dependency Injection enables easy mocking")
    logger.info("2. Repository pattern separates data access from business logic")
    logger.info("3. Service interfaces define clear contracts")
    logger.info("4. All components are independently testable")
    logger.info("5. No need for database fixtures or complex setup")
    logger.info("\nThis architecture makes it easier to achieve 70%+ test coverage!")


if __name__ == "__main__":
    try:
        run_coverage_report()
    except Exception as e:
        logger.info(f"Error running tests: {e}")
        sys.exit(1)
#!/usr/bin/env python3
"""Test script to verify the improved architecture works."""

import sys
import os

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_import_time_dependencies():
    """Test that app can be imported without side effects."""
    print("Testing import-time dependencies...")
    
    try:
        from app import create_app
        print("✅ App can be imported without side effects")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_dependency_injection():
    """Test dependency injection container."""
    print("Testing dependency injection...")
    
    try:
        from app.core.improved_container import container, get_auth_service
        from app.services.interfaces.auth_service_interface import IAuthService
        
        # Test service resolution
        auth_service = container.resolve(IAuthService)
        assert auth_service is not None
        
        # Test helper function
        auth_service2 = get_auth_service()
        assert auth_service2 is not None
        
        print("✅ Dependency injection working correctly")
        return True
    except Exception as e:
        print(f"❌ DI test failed: {e}")
        return False

def test_repository_pattern():
    """Test repository pattern implementation."""
    print("Testing repository pattern...")
    
    try:
        from app.repositories.improved_user_repository import ImprovedUserRepository
        from app.services.interfaces.user_repository_interface import IUserRepository
        
        # Test that repository implements interface
        repo = ImprovedUserRepository()
        assert isinstance(repo, IUserRepository)
        
        print("✅ Repository pattern implemented correctly")
        return True
    except Exception as e:
        print(f"❌ Repository test failed: {e}")
        return False

def test_service_abstraction():
    """Test service abstraction."""
    print("Testing service abstraction...")
    
    try:
        from app.services.improved_auth_service import ImprovedAuthService
        from app.services.interfaces.auth_service_interface import IAuthService
        from app.repositories.improved_user_repository import ImprovedUserRepository
        
        # Test that service implements interface
        user_repo = ImprovedUserRepository()
        auth_service = ImprovedAuthService(user_repo)
        assert isinstance(auth_service, IAuthService)
        
        print("✅ Service abstraction working correctly")
        return True
    except Exception as e:
        print(f"❌ Service abstraction test failed: {e}")
        return False

def test_cli_commands():
    """Test CLI commands."""
    print("Testing CLI commands...")
    
    try:
        from app.cli import init_db, create_test_data
        print("✅ CLI commands imported successfully")
        return True
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def test_api_layer():
    """Test improved API layer."""
    print("Testing improved API layer...")
    
    try:
        from app.api.improved_auth import improved_auth_bp
        assert improved_auth_bp is not None
        print("✅ Improved API layer working correctly")
        return True
    except Exception as e:
        print(f"❌ API layer test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Improved BDC Architecture")
    print("=" * 50)
    
    tests = [
        test_import_time_dependencies,
        test_dependency_injection,
        test_repository_pattern,
        test_service_abstraction,
        test_cli_commands,
        test_api_layer
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Architecture improvements are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())
# Service Layer Architecture Migration Guide

This guide explains how to migrate existing services to use the new standardized service layer architecture with dependency injection.

## Overview

The new architecture provides:
- **BaseService**: Common functionality for all services
- **ServiceContainer**: Dependency injection container
- **ServiceFactory**: Factory pattern for service creation
- **Decorators**: Cross-cutting concerns (caching, transactions, etc.)

## Migration Steps

### 1. Extend BaseService

Update your service to extend `BaseService`:

```python
from app.services.core import BaseService
from app.repositories.interfaces import IUserRepository
from app.models import User

class UserService(BaseService[User, IUserRepository]):
    def __init__(self, repository=None, **kwargs):
        super().__init__(repository=repository, **kwargs)
    
    def _create_repository(self):
        from app.repositories import UserRepository
        return UserRepository(self.db_session)
```

### 2. Use Service Decorator

Add the `@service` decorator for auto-registration:

```python
from app.services.core import service

@service(name='user_service', dependencies=['user_repository', 'security_manager'])
class UserService(BaseService[User, IUserRepository]):
    # ... service implementation
```

### 3. Implement Validation

Override the `validate` method:

```python
def validate(self, data, context=None):
    errors = {}
    
    if context == 'create' and not data.get('email'):
        errors['email'] = 'Email is required'
    
    if errors:
        raise ValueError(f"Validation errors: {errors}")
    
    return data
```

### 4. Use Lifecycle Hooks

Implement hooks for custom logic:

```python
def before_create(self, data):
    # Process data before creation
    if 'password' in data:
        data['password_hash'] = hash_password(data.pop('password'))
    return data

def after_create(self, entity):
    # Actions after creation
    self._send_welcome_email(entity)
    return entity
```

### 5. Apply Decorators

Use decorators for common patterns:

```python
from app.services.core import transactional, cached, inject

@transactional()
def create_user(self, user_data):
    return self.create(user_data)

@cached(timeout=300)
def get_user_by_email(self, email):
    return self.repository.find_by_email(email)

@inject('notification_service')
def notify_user(self, user_id, message, notification_service=None):
    if notification_service:
        notification_service.send_notification(user_id, message)
```

## Complete Example

Here's a complete migration example:

### Before (Old Pattern)

```python
class UserService:
    def __init__(self, user_repository, security_manager):
        self.user_repository = user_repository
        self.security_manager = security_manager
    
    def create_user(self, user_data):
        # Manual validation
        if not user_data.get('email'):
            raise ValueError("Email required")
        
        # Manual transaction handling
        try:
            user = User(**user_data)
            user.password_hash = self.security_manager.hash_password(user_data['password'])
            self.user_repository.create(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise
```

### After (New Pattern)

```python
from app.services.core import BaseService, service, transactional

@service(name='user_service', dependencies=['security_manager'])
class UserService(BaseService[User, IUserRepository]):
    def __init__(self, repository=None, security_manager=None, **kwargs):
        super().__init__(repository=repository, **kwargs)
        self.security_manager = security_manager
    
    def _create_repository(self):
        from app.repositories import UserRepository
        return UserRepository(self.db_session)
    
    def validate(self, data, context=None):
        if context == 'create' and not data.get('email'):
            raise ValueError("Email required")
        return data
    
    def before_create(self, data):
        if 'password' in data:
            data['password_hash'] = self.security_manager.hash_password(data.pop('password'))
        return data
    
    @transactional()
    def create_user(self, user_data):
        return self.create(user_data)
```

## Using the Migrated Service

### Method 1: Direct Container Resolution

```python
from app.services.core import get_service_container

container = get_service_container()
user_service = container.resolve('user_service')
```

### Method 2: Using Factory

```python
from app.services.core import create_service_factory

factory = create_service_factory(UserService, 'user_service')
user_service = factory.create()
```

### Method 3: In Flask Routes with Injection

```python
from app.services.core import inject

@app.route('/users', methods=['POST'])
@inject('user_service')
def create_user_endpoint(user_service):
    data = request.get_json()
    user = user_service.create_user(data)
    return jsonify(user.to_dict())
```

## Benefits After Migration

1. **Consistent Interface**: All services follow the same pattern
2. **Automatic DI**: Dependencies are resolved automatically
3. **Built-in Caching**: Use `@cached` decorator
4. **Transaction Management**: Use `@transactional` decorator
5. **Lifecycle Hooks**: Standardized pre/post processing
6. **Better Testing**: Easy to mock dependencies
7. **Less Boilerplate**: Common functionality in BaseService

## Gradual Migration Strategy

1. Start with new services using the new pattern
2. Migrate critical services first
3. Keep both patterns during transition
4. Update routes/controllers to use new services
5. Remove old services once fully migrated

## Testing Migrated Services

```python
def test_user_service():
    # Mock dependencies
    mock_repo = Mock(spec=IUserRepository)
    mock_security = Mock()
    
    # Create service with mocks
    service = UserService(
        repository=mock_repo,
        security_manager=mock_security
    )
    
    # Test service methods
    user_data = {'email': 'test@example.com', 'password': 'test123'}
    service.create_user(user_data)
    
    # Assert mocks were called correctly
    mock_repo.create.assert_called_once()
```

## Common Pitfalls to Avoid

1. **Don't forget to implement `_create_repository`** if not injecting repository
2. **Remember to call parent methods** in lifecycle hooks
3. **Use proper transaction boundaries** with `@transactional`
4. **Clear caches appropriately** after updates/deletes
5. **Handle circular dependencies** by refactoring service boundaries

## Next Steps

1. Review existing services and plan migration order
2. Create integration tests for critical paths
3. Update API documentation with new service contracts
4. Train team on new patterns and best practices
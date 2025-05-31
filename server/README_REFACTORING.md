# Service Refactoring Guide

## Overview

This guide documents the refactoring process for services in the BDC application, implementing dependency injection, SOLID principles, and modern async patterns.

## Completed Refactorings

### 1. Authentication Service ✅

- **File**: `app/services/auth_service_refactored.py`
- **Interface**: `app/services/interfaces/auth_service_interface.py`
- **Tests**: `tests/test_auth_service_refactored.py`
- **Features**:
  - JWT token management
  - Password reset functionality
  - Two-factor authentication support
  - Session management

### 2. User Service ✅

- **File**: `app/services/user_service_refactored.py`
- **Interface**: `app/services/interfaces/user_service_interface.py`
- **Tests**: `tests/test_user_service_refactored.py`
- **API**: `app/api/users_v2.py`
- **Features**:
  - User CRUD operations
  - Profile management
  - Password management
  - Profile picture upload
  - Beneficiary count for caregivers

## Refactoring Process

### Step 1: Create Interface

```python
from abc import ABC, abstractmethod

class IServiceName(ABC):
    @abstractmethod
    async def method_name(self, param: Type) -> ReturnType:
        pass
```

### Step 2: Create Repository Interface

```python
class IRepositoryName(ABC):
    @abstractmethod
    async def create(self, entity: Entity) -> Entity:
        pass
    
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Entity]:
        pass
```

### Step 3: Implement Repository

```python
class RepositoryName(IRepositoryName):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create(self, entity: Entity) -> Entity:
        self.db_session.add(entity)
        await self.db_session.commit()
        return entity
```

### Step 4: Refactor Service

```python
class ServiceName(IServiceName):
    def __init__(
        self,
        repository: IRepositoryName,
        other_dependency: IOtherDependency
    ):
        self.repository = repository
        self.other_dependency = other_dependency
    
    async def method_name(self, param: Type) -> ReturnType:
        # Implementation using injected dependencies
```

### Step 5: Update Container

```python
def _create_service_name(self) -> IServiceName:
    repository = self.resolve('repository_name')
    other_dependency = self.resolve('other_dependency')
    return ServiceName(repository, other_dependency)
```

### Step 6: Create Tests

```python
@pytest.fixture
def mock_repository():
    repository = Mock()
    repository.create = AsyncMock()
    return repository

@pytest.fixture
def service(mock_repository):
    return ServiceName(repository=mock_repository)

@pytest.mark.asyncio
async def test_method_name(service, mock_repository):
    # Test implementation
```

### Step 7: Create API Endpoints

```python
@blueprint.route('/path', methods=['GET'])
@inject('service_name')
async def endpoint(service: IServiceName):
    result = await service.method_name()
    return jsonify(result)
```

## Dependency Injection Container

The DI container (`app/container.py`) manages all service dependencies:

```python
from app.container import container, inject

# Register a service
container.register('service_name', factory_function, singleton=False)

# Inject into Flask routes
@inject('service_name')
def route_handler(service: IServiceName):
    pass
```

## Testing Strategy

### 1. Unit Tests

- Mock all dependencies
- Test business logic in isolation
- Cover success and error scenarios

### 2. Integration Tests

- Test with real database
- Test API endpoints
- Verify end-to-end flows

### 3. Mock Fixtures

```python
@pytest.fixture
def mock_user_repository():
    repository = Mock()
    repository.get_by_id = AsyncMock()
    return repository
```

## Async Best Practices

1. **Always use async/await**:
   ```python
   async def method():
       result = await async_operation()
       return result
   ```

2. **Handle async contexts**:
   ```python
   async with self.db_session() as session:
       # Database operations
   ```

3. **Avoid blocking operations**:
   ```python
   # Bad
   time.sleep(1)
   
   # Good
   await asyncio.sleep(1)
   ```

## Error Handling

Consistent error handling pattern:

```python
try:
    # Business logic
except ValueError as e:
    logger.warning(f"Validation error: {str(e)}")
    raise
except Exception as e:
    logger.exception(f"Unexpected error: {str(e)}")
    raise
```

## Logging

Use structured logging:

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

logger.info("Operation started", extra={
    "user_id": user_id,
    "operation": "create_user"
})
```

## API Versioning

- Original endpoints: `/api/resource`
- Refactored endpoints: `/api/v2/resource`

This allows gradual migration without breaking existing clients.

## Migration Checklist

When refactoring a service:

- [ ] Create interface
- [ ] Create repository interface
- [ ] Implement repository
- [ ] Refactor service with DI
- [ ] Update container registration
- [ ] Write unit tests
- [ ] Create/update API endpoints
- [ ] Update documentation
- [ ] Test end-to-end flow
- [ ] Update client code

## Next Services to Refactor

1. **Appointment Service**
   - Booking management
   - Calendar integration
   - Availability checking

2. **Notification Service**
   - Email notifications
   - SMS notifications
   - Push notifications

3. **Document Service**
   - File upload/download
   - Document versioning
   - Access control

4. **Evaluation Service**
   - Assessment management
   - Scoring system
   - Report generation

## Benefits of Refactoring

1. **Testability**: Easy to mock dependencies
2. **Maintainability**: Clear separation of concerns
3. **Scalability**: Easy to swap implementations
4. **Type Safety**: Strong typing with interfaces
5. **Performance**: Async operations throughout
6. **Consistency**: Uniform patterns across services

## Resources

- [Dependency Injection in Python](https://python-dependency-injector.readthedocs.io/)
- [SOLID Principles](https://www.digitalocean.com/community/conceptual_articles/s-o-l-i-d-the-five-principles-of-object-oriented-design)
- [Async Python Best Practices](https://docs.python.org/3/library/asyncio.html)
- [Flask Async Views](https://flask.palletsprojects.com/en/2.3.x/async-await/)

## Contributing

When adding new refactored services:

1. Follow the established patterns
2. Update this documentation
3. Ensure comprehensive test coverage
4. Document any deviations from patterns
5. Update the container configuration
# Calendar Service Migration Guide

This guide helps you migrate from the old `CalendarService` to the new `CalendarServiceRefactored`.

## Key Changes

### 1. Dependency Injection
- **Old**: Class methods with Flask dependencies
- **New**: Instance methods with injected dependencies

```python
# Old
from app.services.calendar_service import CalendarService
auth_url = CalendarService.get_authorization_url(user_id)

# New
from app.services.calendar_service_refactored import CalendarServiceRefactored
from app.extensions import db

calendar_service = CalendarServiceRefactored(
    db_session=db.session,
    client_secrets_path='/path/to/client_secret.json',
    redirect_uri='http://localhost/callback'
)
auth_url = calendar_service.get_authorization_url(user_id)
```

### 2. Return Types
- **Old**: Returns URLs/IDs directly or None on failure
- **New**: Returns dictionaries with structured responses

```python
# Old
event_id = CalendarService.create_calendar_event(user_id, appointment_dict)
if not event_id:
    # Handle error

# New
try:
    result = calendar_service.create_event(user_id, event)
    event_id = result['event_id']
except (NotFoundException, ValidationException, ExternalServiceException) as e:
    # Handle specific error types
```

### 3. Event Data Structure
- **Old**: Pass dictionaries with appointment data
- **New**: Use `CalendarEvent` dataclass

```python
# Old
appointment = {
    'title': 'Meeting',
    'description': 'Description',
    'start_time': datetime_obj,
    'end_time': datetime_obj,
    'attendees': ['email@example.com']
}

# New
from app.services.calendar_service_refactored import CalendarEvent

event = CalendarEvent(
    title='Meeting',
    description='Description',
    start_time=datetime_obj,
    end_time=datetime_obj,
    attendees=['email@example.com']
)
```

### 4. Error Handling
- **Old**: Returns None or False on errors, logs to Flask app logger
- **New**: Raises specific exceptions with meaningful messages

```python
# Old
if not CalendarService.handle_callback(user_id, code, state):
    # Generic error handling

# New
try:
    result = calendar_service.handle_oauth_callback(user_id, code, state)
except NotFoundException as e:
    # User has no integration
except ValidationException as e:
    # Invalid state or code
except ExternalServiceException as e:
    # External service error
```

### 5. Method Name Changes
| Old Method | New Method |
|------------|------------|
| `get_authorization_url()` | `get_authorization_url()` |
| `handle_callback()` | `handle_oauth_callback()` |
| `create_calendar_event()` | `create_event()` |
| `update_calendar_event()` | `update_event()` |
| `delete_calendar_event()` | `delete_event()` |
| `get_calendar_events()` | `get_events()` |
| `get_credentials()` | `is_connected()` (for checking connection status) |

## Migration Steps

1. **Update imports**:
   ```python
   # Replace
   from app.services.calendar_service import CalendarService
   
   # With
   from app.services.calendar_service_refactored import CalendarServiceRefactored, CalendarEvent
   ```

2. **Create service instance**:
   ```python
   # In your route or service initialization
   calendar_service = CalendarServiceRefactored(
       db_session=db.session,
       client_secrets_path=os.path.join(app.root_path, 'credentials', 'client_secret.json'),
       redirect_uri=url_for('appointments.oauth2callback', _external=True)
   )
   ```

3. **Update method calls**:
   ```python
   # Example: Creating an event
   # Old
   event_id = CalendarService.create_calendar_event(user_id, {
       'title': title,
       'start_time': start,
       'end_time': end
   })
   
   # New
   event = CalendarEvent(
       title=title,
       description=description,
       start_time=start,
       end_time=end,
       attendees=attendees
   )
   result = calendar_service.create_event(user_id, event)
   event_id = result['event_id']
   ```

4. **Update error handling**:
   ```python
   # Wrap service calls in try-except blocks
   try:
       result = calendar_service.create_event(user_id, event)
   except NotFoundException:
       flash('Please connect your Google Calendar first', 'warning')
   except ValidationException as e:
       flash(f'Invalid event data: {str(e)}', 'error')
   except ExternalServiceException:
       flash('Failed to create event in Google Calendar', 'error')
   ```

## Testing

The refactored service includes comprehensive unit tests. Run them with:
```bash
pytest tests/test_calendar_service_refactored.py -v --cov=app.services.calendar_service_refactored
```

## Benefits of Migration

1. **Better testability**: Dependency injection allows easy mocking
2. **Type safety**: Full type hints throughout
3. **Clearer errors**: Specific exceptions instead of None/False returns
4. **No Flask coupling**: Can be used outside Flask context
5. **Structured responses**: Consistent dictionary responses
6. **Better separation of concerns**: OAuth logic separated from calendar operations
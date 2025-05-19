"""Test validation."""

from app.schemas.auth import LoginSchema
from marshmallow import ValidationError

# Test data
test_data = {
    "email": "admin@bdc.com",
    "password": "Admin123!",
    "remember": False
}

schema = LoginSchema()

try:
    result = schema.load(test_data)
    print("Validation successful!")
    print(f"Result: {result}")
except ValidationError as e:
    print(f"Validation error: {e.messages}")
except Exception as e:
    print(f"Error: {e}")
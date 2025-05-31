#!/usr/bin/env python
"""Test auth error directly."""

from app import create_app
from app.services import AuthService

app = create_app()

with app.app_context():
    try:
        result = AuthService.login('admin@bdc.com', 'Admin123!', False)
        print(f"Login result: {result}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
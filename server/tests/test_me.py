#!/usr/bin/env python3
"""Live HTTP test for /me endpoint.

Skip during automated unit tests.
"""

import pytest

pytest.skip("Live HTTP test – skip during automated unit tests", allow_module_level=True)

# Original code for manual execution is commented below.

# import requests, json
# login_url = "http://localhost:5001/api/auth/login"
# me_url = "http://localhost:5001/api/users/me"
# headers = {"Content-Type": "application/json", "Origin": "http://localhost:5173"}
# login_data = {"email": "admin@bdc.com", "password": "Admin123!"}
# ...
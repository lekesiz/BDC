#!/usr/bin/env python3
"""Live HTTP test for notification endpoint – skipped in CI."""

import pytest

pytest.skip("Live HTTP notification test – skip during automated unit tests", allow_module_level=True)

# Original code kept below for manual execution.
# import requests, json
# ...
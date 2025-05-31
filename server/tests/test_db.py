#!/usr/bin/env python3
"""Manual DB inspection script (skipped in automated tests)."""

import pytest

# Skip during pytest collection
pytest.skip("Diagnostic DB script – skip during automated unit tests", allow_module_level=True)

# Original diagnostic code retained below for on-demand manual runs.

import sys  # noqa: E402
sys.path.insert(0, '/Users/mikail/Desktop/BDC/server')  # noqa: E402

from app.extensions import db  # noqa: E402
from app import create_app  # noqa: E402
from app.models.beneficiary import Beneficiary, Note, BeneficiaryDocument  # noqa: E402
from app.models.document import Document  # noqa: E402
from app.models.evaluation import Evaluation  # noqa: E402

# Create app with default config (requires running DB when executed manually)
app = create_app()  # noqa: E402

with app.app_context():  # noqa: E402
    db.create_all()
    print("✓ Tables created successfully (manual run)")
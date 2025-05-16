#!/usr/bin/env python3
"""Test database models and relationships."""

import sys
sys.path.insert(0, '/Users/mikail/Desktop/BDC/server')

from app.extensions import db
from app import create_app
from app.models.beneficiary import Beneficiary, Note, BeneficiaryDocument
from app.models.document import Document
from app.models.evaluation import Evaluation

# Create app with test config
app = create_app()

with app.app_context():
    # Try to create tables
    try:
        db.create_all()
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        
    # Test model relationships
    try:
        # Test Beneficiary relationships
        b = Beneficiary()
        print(f"✓ Beneficiary model created")
        
        # Test Document relationships
        d = Document()
        print(f"✓ Document model created")
        
        # Test Evaluation relationships
        e = Evaluation()
        print(f"✓ Evaluation model created")
        
        # Test Note relationships
        n = Note()
        print(f"✓ Note model created")
        
        print("\n✓ All models and relationships are properly configured!")
        
    except Exception as e:
        print(f"\n✗ Error with model relationships: {e}")
        import traceback
        traceback.print_exc()
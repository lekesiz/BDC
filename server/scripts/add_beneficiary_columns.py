#!/usr/bin/env python
"""Add missing beneficiary columns."""

import sqlite3

from app.utils.logging import logger

# Adjust the path based on your app's configuration
db_path = 'app.db'

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get existing columns
cursor.execute("PRAGMA table_info(beneficiaries)")
existing_columns = [row[1] for row in cursor.fetchall()]
logger.info(f"Existing columns: {existing_columns}")

# Columns to add
columns_to_add = [
    ('state', 'TEXT'),
    ('nationality', 'TEXT'),
    ('native_language', 'TEXT'),
    ('category', 'TEXT'),
    ('bio', 'TEXT'),
    ('goals', 'TEXT'),
    ('notes', 'TEXT'),
    ('referral_source', 'TEXT'),
    ('custom_fields', 'TEXT')
]

# Add missing columns
for column_name, column_type in columns_to_add:
    if column_name not in existing_columns:
        try:
            cursor.execute(f"ALTER TABLE beneficiaries ADD COLUMN {column_name} {column_type}")
            logger.info(f"Added column: {column_name}")
        except sqlite3.OperationalError as e:
            logger.info(f"Error adding column {column_name}: {e}")
    else:
        logger.info(f"Column already exists: {column_name}")

# Commit changes
conn.commit()
conn.close()

logger.info("Done!")
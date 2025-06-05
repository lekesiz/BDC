#!/usr/bin/env python3
"""Add user preference fields to database."""

import sqlite3
import os

from app.utils.logging import logger

# Get database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Add new columns to users table
    columns_to_add = [
        ('email_notifications', 'BOOLEAN DEFAULT TRUE'),
        ('push_notifications', 'BOOLEAN DEFAULT FALSE'),
        ('sms_notifications', 'BOOLEAN DEFAULT FALSE'),
        ('language', 'VARCHAR(10) DEFAULT "en"'),
        ('theme', 'VARCHAR(20) DEFAULT "light"')
    ]
    
    for column_name, column_def in columns_to_add:
        try:
            cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_def}')
            logger.info(f"Added column: {column_name}")
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e):
                logger.info(f"Column already exists: {column_name}")
            else:
                raise
    
    # Commit changes
    conn.commit()
    logger.info("Database updated successfully!")
    
except Exception as e:
    logger.info(f"Error: {e}")
    conn.rollback()
    
finally:
    conn.close()
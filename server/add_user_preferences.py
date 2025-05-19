#!/usr/bin/env python3
"""Add user preference fields to database."""

import sqlite3
import os

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
            print(f'Added column: {column_name}')
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e):
                print(f'Column already exists: {column_name}')
            else:
                raise
    
    # Commit changes
    conn.commit()
    print('Database updated successfully!')
    
except Exception as e:
    print(f'Error: {e}')
    conn.rollback()
    
finally:
    conn.close()
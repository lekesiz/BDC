#!/usr/bin/env python3
"""Migration script to add user preference columns to the database."""

from app import create_app
from app.extensions import db
from sqlalchemy import text
import sqlite3

from app.utils.logging import logger

app = create_app()

with app.app_context():
    # Get database path from the app config
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    # Connect directly to SQLite to add columns
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the current table info
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [column[1] for column in cursor.fetchall()]
    
    # Define new columns
    new_columns = [
        ("email_notifications", "BOOLEAN DEFAULT 1"),
        ("push_notifications", "BOOLEAN DEFAULT 0"),
        ("sms_notifications", "BOOLEAN DEFAULT 0"),
        ("language", "VARCHAR(10) DEFAULT 'en'"),
        ("theme", "VARCHAR(20) DEFAULT 'light'")
    ]
    
    # Add each column if it doesn't exist
    for column_name, column_def in new_columns:
        if column_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
                logger.info(f"Added column: {column_name}")
            except sqlite3.OperationalError as e:
                logger.info(f"Column {column_name} may already exist: {e}")
    
    # Commit the changes
    conn.commit()
    conn.close()
    
    logger.info("Migration completed successfully!")
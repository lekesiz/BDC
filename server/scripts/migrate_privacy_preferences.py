#!/usr/bin/env python3
"""Migration script to add privacy preference columns to the database."""

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
    
    # Check if user_preferences table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_preferences'")
    if not cursor.fetchone():
        # Create the table if it doesn't exist
        cursor.execute("""
            CREATE TABLE user_preferences (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                theme VARCHAR(20) DEFAULT 'light',
                language VARCHAR(10) DEFAULT 'en',
                notifications_enabled BOOLEAN DEFAULT 1,
                email_notifications BOOLEAN DEFAULT 1,
                sms_notifications BOOLEAN DEFAULT 0,
                push_notifications BOOLEAN DEFAULT 1,
                profile_visibility VARCHAR(20) DEFAULT 'all',
                show_online_status BOOLEAN DEFAULT 1,
                share_activity BOOLEAN DEFAULT 1,
                allow_data_collection BOOLEAN DEFAULT 1,
                sidebar_collapsed BOOLEAN DEFAULT 0,
                density VARCHAR(20) DEFAULT 'normal',
                accent_color VARCHAR(20) DEFAULT 'blue',
                font_size VARCHAR(20) DEFAULT 'medium',
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        logger.info("Created user_preferences table")
    else:
        # Get the current table info
        cursor.execute("PRAGMA table_info(user_preferences)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # Define new columns
        new_columns = [
            ("profile_visibility", "VARCHAR(20) DEFAULT 'all'"),
            ("show_online_status", "BOOLEAN DEFAULT 1"),
            ("share_activity", "BOOLEAN DEFAULT 1"),
            ("allow_data_collection", "BOOLEAN DEFAULT 1"),
            ("sidebar_collapsed", "BOOLEAN DEFAULT 0"),
            ("density", "VARCHAR(20) DEFAULT 'normal'"),
            ("accent_color", "VARCHAR(20) DEFAULT 'blue'"),
            ("font_size", "VARCHAR(20) DEFAULT 'medium'")
        ]
        
        # Add each column if it doesn't exist
        for column_name, column_def in new_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE user_preferences ADD COLUMN {column_name} {column_def}")
                    logger.info(f"Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    logger.info(f"Column {column_name} may already exist: {e}")
    
    # Commit the changes
    conn.commit()
    conn.close()
    
    logger.info("Migration completed successfully!")
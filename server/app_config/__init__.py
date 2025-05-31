"""Configuration package for BDC application."""

# Import config classes from the main config.py file
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import from the config.py file in the parent directory
from config import Config, DevelopmentConfig, TestingConfig, ProductionConfig

__all__ = ['Config', 'DevelopmentConfig', 'TestingConfig', 'ProductionConfig']
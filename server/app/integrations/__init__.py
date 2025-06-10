"""
Third-party integrations package for BDC project.

This package provides a comprehensive system for integrating with various
third-party services including calendars, payments, video conferencing,
email services, storage providers, and authentication providers.
"""

from .base import BaseIntegration, IntegrationError, IntegrationConfig
from .config import IntegrationManager
from .registry import IntegrationRegistry

__all__ = [
    'BaseIntegration',
    'IntegrationError', 
    'IntegrationConfig',
    'IntegrationManager',
    'IntegrationRegistry'
]
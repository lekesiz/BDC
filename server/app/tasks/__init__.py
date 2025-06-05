"""Celery tasks module."""

from celery import shared_task

# Import all tasks to register them
from .notifications import *
from .evaluations import *
from .maintenance import *
from .reports import *
from .email import *
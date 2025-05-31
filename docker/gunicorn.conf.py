"""Gunicorn production configuration for BDC application."""

import multiprocessing
import os

# Server Socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker Processes
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "eventlet"
worker_connections = 1000
max_requests = int(os.environ.get('GUNICORN_MAX_REQUESTS', 1000))
max_requests_jitter = int(os.environ.get('GUNICORN_MAX_REQUESTS_JITTER', 100))
preload_app = True

# Socket Settings
timeout = 30
keepalive = 2
graceful_timeout = 30

# Logging
loglevel = "info"
errorlog = "/var/log/bdc/gunicorn_error.log"
accesslog = "/var/log/bdc/gunicorn_access.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Naming
proc_name = "bdc_gunicorn"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
enable_stdio_inheritance = True

# SSL (if using direct SSL termination)
keyfile = os.environ.get('SSL_KEY_PATH')
certfile = os.environ.get('SSL_CERT_PATH')

def when_ready(server):
    """Called when the server is started."""
    server.log.info("BDC Application server is ready. Listening on: %s", server.address)

def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called before a worker is forked."""
    server.log.info("Worker %s spawned", worker.pid)

def post_fork(server, worker):
    """Called after a worker is forked."""
    server.log.info("Worker %s initialized", worker.pid)

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info("Worker %s aborted", worker.pid)

# Environment Variables for Application
raw_env = [
    f'FLASK_ENV={os.environ.get("FLASK_ENV", "production")}',
    f'DATABASE_URL={os.environ.get("DATABASE_URL", "")}',
    f'REDIS_URL={os.environ.get("REDIS_URL", "")}',
    f'SECRET_KEY={os.environ.get("SECRET_KEY", "")}',
]
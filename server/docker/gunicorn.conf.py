"""Gunicorn configuration for production deployment."""

import os
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = int(os.environ.get('WORKER_PROCESSES', multiprocessing.cpu_count() * 2 + 1))
worker_class = "gevent"
worker_connections = int(os.environ.get('WORKER_CONNECTIONS', 1000))
max_requests = 1000
max_requests_jitter = 50
timeout = int(os.environ.get('WORKER_TIMEOUT', 30))
keepalive = int(os.environ.get('WORKER_KEEPALIVE', 5))

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'bdc_app'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = '/tmp'

# SSL
keyfile = os.environ.get('SSL_KEY_PATH')
certfile = os.environ.get('SSL_CERT_PATH')
ca_certs = os.environ.get('SSL_CA_BUNDLE_PATH')

# Worker configuration
preload_app = True
enable_stdio_inheritance = True

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

def when_ready(server):
    """Called when the server is started."""
    server.log.info("BDC Server is ready. Listening on: %s", server.address)

def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called after a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker process is killed."""
    worker.log.info("Worker process %s aborted", worker.pid)
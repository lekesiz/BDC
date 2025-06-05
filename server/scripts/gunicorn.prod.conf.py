# Gunicorn production configuration

import os
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
loglevel = "info"
accesslog = "/app/logs/gunicorn-access.log"
errorlog = "/app/logs/gunicorn-error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "bdc-backend"

# Worker temporary directory
worker_tmp_dir = "/dev/shm"

# SSL (when certificates are available)
# keyfile = "/etc/ssl/private/server.key"
# certfile = "/etc/ssl/certs/server.crt"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance tuning
def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

# Environment variables
raw_env = [
    'FLASK_ENV=production',
    'PYTHONPATH=/app',
]
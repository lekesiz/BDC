# Multi-stage Docker build for production BDC application
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    redis-tools \
    curl \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r bdc && useradd -r -g bdc -d /app -s /bin/bash bdc

# Set work directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt requirements-production.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-production.txt

# Production stage
FROM base as production

# Copy application code
COPY --chown=bdc:bdc . .

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/instance \
    && chown -R bdc:bdc /app

# Switch to non-root user
USER bdc

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start command
CMD ["gunicorn", "--config", "docker/gunicorn.conf.py", "wsgi:application"]

# Development stage
FROM base as development

# Install additional development dependencies
COPY requirements-test.txt ./
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy application code
COPY --chown=bdc:bdc . .

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/instance \
    && chown -R bdc:bdc /app

# Switch to non-root user
USER bdc

# Start command for development
CMD ["python", "run_app.py"]
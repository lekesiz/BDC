# Multi-stage Docker build for BDC Backend
FROM python:3.11-slim as base

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Development stage
FROM base as development

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install development dependencies
RUN pip install --no-cache-dir flask-debugtoolbar flask-shell-ipython

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs /app/instance && \
    chown -R appuser:appuser /app

# Create health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:5000/api/health || exit 1' > /usr/local/bin/healthcheck.sh && \
    chmod +x /usr/local/bin/healthcheck.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Development command with hot reload
CMD ["python", "run_local.py"]

# Production stage
FROM base as production

# Install production dependencies only
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs /app/instance && \
    chown -R appuser:appuser /app

# Create health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:5000/api/health || exit 1' > /usr/local/bin/healthcheck.sh && \
    chmod +x /usr/local/bin/healthcheck.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Production command with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "30", "wsgi:app"]
# ====================================
# BDC PRODUCTION DOCKERFILE
# Multi-stage build for optimized production
# ====================================

# =====================================
# Stage 1: Backend Build
# =====================================
FROM python:3.11-slim-bullseye as backend-builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user and directory
RUN useradd --create-home --shell /bin/bash bdc
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements-production.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements-production.txt

# =====================================
# Stage 2: Frontend Build
# =====================================
FROM node:18-alpine as frontend-builder

WORKDIR /app/client

# Copy package files
COPY client/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY client/ .

# Build for production
RUN npm run build

# =====================================
# Stage 3: Production Runtime
# =====================================
FROM python:3.11-slim-bullseye as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    PATH="/home/bdc/.local/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Create app user and directories
RUN useradd --create-home --shell /bin/bash bdc && \
    mkdir -p /app /var/log/bdc /var/uploads/bdc && \
    chown -R bdc:bdc /app /var/log/bdc /var/uploads/bdc

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy built frontend from builder
COPY --from=frontend-builder /app/client/dist /app/static

# Switch to app user
USER bdc
WORKDIR /app

# Copy backend application
COPY --chown=bdc:bdc server/ .

# Copy configuration files
COPY --chown=bdc:bdc docker/gunicorn.conf.py .
COPY --chown=bdc:bdc config/production.py config/

# Create necessary directories
RUN mkdir -p logs uploads

# Switch back to root for system configuration
USER root

# Copy Nginx configuration
COPY docker/nginx.conf /etc/nginx/sites-available/default

# Copy supervisor configuration
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create health check script
COPY docker/healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
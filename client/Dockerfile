# Multi-stage Docker build for BDC Frontend
FROM node:18-alpine as base

# Install system dependencies
RUN apk add --no-cache \
    git \
    curl \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S appuser && \
    adduser -S appuser -u 1001 -G appuser

# Development stage
FROM base as development

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies)
RUN npm ci --include=dev

# Copy application code
COPY . .

# Set ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose Vite dev server port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5173 || exit 1

# Development command with hot reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

# Builder stage for production
FROM base as builder

# Copy package files
COPY package*.json ./

# Install production dependencies only
RUN npm ci --only=production --omit=dev

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Production stage with Nginx
FROM nginx:1.25-alpine as production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create non-root user for Nginx
RUN addgroup -g 1001 -S nginx && \
    adduser -S nginx -u 1001 -G nginx

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Create health check script
RUN echo '#!/bin/sh\ncurl -f http://localhost:80 || exit 1' > /usr/local/bin/healthcheck.sh && \
    chmod +x /usr/local/bin/healthcheck.sh

# Switch to non-root user
USER nginx

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# Production command
CMD ["nginx", "-g", "daemon off;"]
#!/bin/bash
# Deployment script for BDC application

set -e

# Set default values
ENVIRONMENT=${1:-"development"}
TAG=${2:-"latest"}
REPO="ghcr.io/organization/bdc"  # Replace with your actual repository

# Configuration based on environment
if [ "$ENVIRONMENT" == "production" ]; then
    TARGET_HOST=${PROD_HOST:-""}
    TARGET_USER=${PROD_USER:-""}
    TARGET_DIR=${PROD_DIR:-"/opt/bdc"}
    COMPOSE_FILE="docker-compose.prod.yml"
elif [ "$ENVIRONMENT" == "development" ]; then
    TARGET_HOST=${DEV_HOST:-""}
    TARGET_USER=${DEV_USER:-""}
    TARGET_DIR=${DEV_DIR:-"/opt/bdc-dev"}
    COMPOSE_FILE="docker-compose.dev.yml"
else
    echo "Unknown environment: $ENVIRONMENT"
    echo "Usage: $0 [development|production] [tag]"
    exit 1
fi

# Ensure host is specified
if [ -z "$TARGET_HOST" ]; then
    echo "Error: Target host not specified."
    echo "Set the appropriate environment variable (DEV_HOST or PROD_HOST)."
    exit 1
fi

echo "Deploying to $ENVIRONMENT environment on $TARGET_HOST..."

# Copy docker-compose file to target
scp "$COMPOSE_FILE" "$TARGET_USER@$TARGET_HOST:$TARGET_DIR/docker-compose.yml"

# SSH to target and update the application
ssh "$TARGET_USER@$TARGET_HOST" "cd $TARGET_DIR && \
    echo \"Pulling latest images...\" && \
    docker pull $REPO/bdc-server:$TAG && \
    docker pull $REPO/bdc-client:$TAG && \
    echo \"Restarting containers...\" && \
    docker-compose up -d && \
    echo \"Cleaning up old images...\" && \
    docker image prune -f"

echo "Deployment completed successfully."
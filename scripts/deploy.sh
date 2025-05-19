#!/bin/bash
# Deployment script for BDC application

set -e

# Set default values
ENVIRONMENT=${1:-"development"}
TAG=${2:-"latest"}
GH_REPO=${GITHUB_REPOSITORY:-"organization/bdc"}
REPO="ghcr.io/${GH_REPO}"

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
elif [ "$ENVIRONMENT" == "staging" ]; then
    TARGET_HOST=${STAGING_HOST:-""}
    TARGET_USER=${STAGING_USER:-""}
    TARGET_DIR=${STAGING_DIR:-"/opt/bdc-staging"}
    COMPOSE_FILE="docker-compose.staging.yml"
else
    echo "Unknown environment: $ENVIRONMENT"
    echo "Usage: $0 [development|staging|production] [tag]"
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
scp "docker/$COMPOSE_FILE" "$TARGET_USER@$TARGET_HOST:$TARGET_DIR/docker-compose.yml"

# Copy environment file if it exists
if [ -f ".env.$ENVIRONMENT" ]; then
    scp ".env.$ENVIRONMENT" "$TARGET_USER@$TARGET_HOST:$TARGET_DIR/.env"
fi

# SSH to target and update the application
ssh "$TARGET_USER@$TARGET_HOST" "cd $TARGET_DIR && \
    echo \"Pulling latest images...\" && \
    docker pull $REPO/bdc-server:$TAG && \
    docker pull $REPO/bdc-client:$TAG && \
    echo \"Running database migrations...\" && \
    docker-compose exec -T backend flask db upgrade && \
    echo \"Restarting containers...\" && \
    docker-compose up -d && \
    echo \"Cleaning up old images...\" && \
    docker image prune -f && \
    echo \"Waiting for services to be healthy...\" && \
    sleep 10 && \
    docker-compose ps"

echo "Deployment completed successfully."

# Run smoke tests
if [ "$ENVIRONMENT" == "production" ]; then
    echo "Running smoke tests..."
    ./scripts/smoke_test.sh
fi
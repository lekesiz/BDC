#!/bin/bash
# Ansible deployment wrapper script

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Parse arguments
ENVIRONMENT=${1:-"staging"}
ACTION=${2:-"deploy"}
VERSION=${3:-"latest"}

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
    echo -e "${RED}Invalid environment: $ENVIRONMENT${NC}"
    echo "Usage: $0 [staging|production] [deploy|check|rollback] [version]"
    exit 1
fi

echo -e "${GREEN}Starting $ACTION for $ENVIRONMENT environment${NC}"

# Set ansible variables
export ANSIBLE_HOST_KEY_CHECKING=False
export ANSIBLE_FORCE_COLOR=True

# Common variables
EXTRA_VARS="target_env=$ENVIRONMENT app_version=$VERSION"

case $ACTION in
    "deploy")
        echo "Deploying version $VERSION to $ENVIRONMENT..."
        ansible-playbook -i inventory.ini playbook.yml \
            --extra-vars "$EXTRA_VARS" \
            --tags "deploy"
        ;;
    
    "check")
        echo "Running pre-deployment checks..."
        ansible-playbook -i inventory.ini playbook.yml \
            --extra-vars "$EXTRA_VARS" \
            --check
        ;;
    
    "rollback")
        echo "Rolling back $ENVIRONMENT deployment..."
        ansible-playbook -i inventory.ini rollback.yml \
            --extra-vars "$EXTRA_VARS"
        ;;
    
    "status")
        echo "Checking status of $ENVIRONMENT..."
        ansible -i inventory.ini $ENVIRONMENT -m shell \
            -a "cd /opt/bdc && docker-compose ps"
        ;;
    
    "backup")
        echo "Creating backup of $ENVIRONMENT..."
        ansible -i inventory.ini $ENVIRONMENT -m shell \
            -a "/opt/bdc/scripts/backup.sh"
        ;;
    
    *)
        echo -e "${RED}Unknown action: $ACTION${NC}"
        echo "Valid actions: deploy, check, rollback, status, backup"
        exit 1
        ;;
esac

echo -e "${GREEN}Operation completed successfully${NC}"
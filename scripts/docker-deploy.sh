#!/bin/bash

# BDC Docker Portable Deployment Script
# Deploys BDC application anywhere with Docker support

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${PROJECT_DIR}/.env"
ENV_TEMPLATE="${PROJECT_DIR}/.env.production.template"
COMPOSE_FILE="${PROJECT_DIR}/docker-compose.portable.yml"
DATA_DIR="${PROJECT_DIR}/data"

# Default values
DEPLOYMENT_MODE="production"
ENABLE_MONITORING=false
SKIP_BUILD=false
FORCE_RECREATE=false
DRY_RUN=false

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS")
            echo -e "${GREEN}✓${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}✗${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ${NC} $message"
            ;;
        "STEP")
            echo -e "${PURPLE}▶${NC} $message"
            ;;
    esac
}

# Function to show usage
show_usage() {
    cat << EOF
BDC Docker Portable Deployment Script

Usage: $0 [OPTIONS]

Options:
    -m, --mode MODE         Deployment mode (production|development) [default: production]
    -M, --monitoring        Enable monitoring services (Prometheus, Grafana)
    -s, --skip-build        Skip building images (use existing images)
    -f, --force-recreate    Force recreate containers
    -d, --dry-run          Show what would be done without executing
    -h, --help             Show this help message

Examples:
    $0                                    # Basic production deployment
    $0 -M                                 # Production with monitoring
    $0 -m development                     # Development mode
    $0 -f -M                             # Force recreate with monitoring
    $0 -d -M                             # Dry run with monitoring

Environment:
    Copy .env.production.template to .env and configure your values before deployment.

Data Directory:
    Data will be stored in: $DATA_DIR
    Ensure this directory has proper permissions and sufficient space.

EOF
}

# Function to parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--mode)
                DEPLOYMENT_MODE="$2"
                shift 2
                ;;
            -M|--monitoring)
                ENABLE_MONITORING=true
                shift
                ;;
            -s|--skip-build)
                SKIP_BUILD=true
                shift
                ;;
            -f|--force-recreate)
                FORCE_RECREATE=true
                shift
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_status "ERROR" "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Function to validate prerequisites
validate_prerequisites() {
    print_status "STEP" "Validating prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker >/dev/null 2>&1; then
        print_status "ERROR" "Docker is not installed or not in PATH"
        return 1
    fi
    
    # Check if Docker Compose is available
    if ! docker compose version >/dev/null 2>&1; then
        print_status "ERROR" "Docker Compose is not available"
        return 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_status "ERROR" "Docker daemon is not running"
        return 1
    fi
    
    # Check if compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        print_status "ERROR" "Docker Compose file not found: $COMPOSE_FILE"
        return 1
    fi
    
    print_status "SUCCESS" "Prerequisites validated"
    return 0
}

# Function to check and setup environment
setup_environment() {
    print_status "STEP" "Setting up environment..."
    
    # Check if .env file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        if [[ -f "$ENV_TEMPLATE" ]]; then
            print_status "WARNING" ".env file not found, copying from template"
            cp "$ENV_TEMPLATE" "$ENV_FILE"
            print_status "INFO" "Please edit $ENV_FILE with your configuration"
            
            if [[ "$DRY_RUN" == "false" ]]; then
                read -p "Continue with default values? (y/N): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    print_status "INFO" "Please configure $ENV_FILE and run again"
                    exit 0
                fi
            fi
        else
            print_status "ERROR" "Neither .env nor .env.production.template found"
            return 1
        fi
    fi
    
    # Validate required environment variables
    local required_vars=(
        "DATABASE_PASSWORD"
        "REDIS_PASSWORD"
        "SECRET_KEY"
        "JWT_SECRET_KEY"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" "$ENV_FILE" || grep -q "^${var}=.*your-.*" "$ENV_FILE"; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        print_status "WARNING" "The following variables need configuration in $ENV_FILE:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        
        if [[ "$DRY_RUN" == "false" ]]; then
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 0
            fi
        fi
    fi
    
    print_status "SUCCESS" "Environment setup complete"
    return 0
}

# Function to setup data directories
setup_data_directories() {
    print_status "STEP" "Setting up data directories..."
    
    local directories=(
        "$DATA_DIR"
        "$DATA_DIR/postgres"
        "$DATA_DIR/redis"
        "$DATA_DIR/uploads"
        "$DATA_DIR/logs"
        "$DATA_DIR/nginx-logs"
        "$DATA_DIR/prometheus"
        "$DATA_DIR/grafana"
    )
    
    for dir in "${directories[@]}"; do
        if [[ "$DRY_RUN" == "true" ]]; then
            print_status "INFO" "Would create directory: $dir"
        else
            mkdir -p "$dir"
            chmod 755 "$dir"
            print_status "INFO" "Created directory: $dir"
        fi
    done
    
    # Set proper permissions for specific directories
    if [[ "$DRY_RUN" == "false" ]]; then
        # PostgreSQL data directory needs specific permissions
        chmod 700 "$DATA_DIR/postgres" 2>/dev/null || true
        
        # Grafana data directory
        chmod 777 "$DATA_DIR/grafana" 2>/dev/null || true
    fi
    
    print_status "SUCCESS" "Data directories setup complete"
    return 0
}

# Function to build images
build_images() {
    if [[ "$SKIP_BUILD" == "true" ]]; then
        print_status "INFO" "Skipping image build as requested"
        return 0
    fi
    
    print_status "STEP" "Building Docker images..."
    
    local build_args=(
        "--file" "$COMPOSE_FILE"
        "build"
    )
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_status "INFO" "Would run: docker compose ${build_args[*]}"
        return 0
    fi
    
    # Enable BuildKit for better performance
    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1
    
    if docker compose "${build_args[@]}"; then
        print_status "SUCCESS" "Images built successfully"
    else
        print_status "ERROR" "Image build failed"
        return 1
    fi
    
    return 0
}

# Function to deploy services
deploy_services() {
    print_status "STEP" "Deploying services..."
    
    local deploy_args=(
        "--file" "$COMPOSE_FILE"
        "up" "-d"
    )
    
    # Add profiles if monitoring is enabled
    if [[ "$ENABLE_MONITORING" == "true" ]]; then
        deploy_args+=("--profile" "monitoring")
    fi
    
    # Add force recreate if requested
    if [[ "$FORCE_RECREATE" == "true" ]]; then
        deploy_args+=("--force-recreate")
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_status "INFO" "Would run: docker compose ${deploy_args[*]}"
        return 0
    fi
    
    if docker compose "${deploy_args[@]}"; then
        print_status "SUCCESS" "Services deployed successfully"
    else
        print_status "ERROR" "Service deployment failed"
        return 1
    fi
    
    return 0
}

# Function to wait for services to be ready
wait_for_services() {
    if [[ "$DRY_RUN" == "true" ]]; then
        print_status "INFO" "Would wait for services to be ready"
        return 0
    fi
    
    print_status "STEP" "Waiting for services to be ready..."
    
    local services=("postgres" "redis" "backend" "frontend")
    local max_wait=300  # 5 minutes
    local wait_time=0
    
    for service in "${services[@]}"; do
        print_status "INFO" "Waiting for $service to be healthy..."
        
        while [[ $wait_time -lt $max_wait ]]; do
            if docker compose --file "$COMPOSE_FILE" ps "$service" | grep -q "healthy\|Up"; then
                print_status "SUCCESS" "$service is ready"
                break
            fi
            
            sleep 5
            wait_time=$((wait_time + 5))
            
            if [[ $wait_time -ge $max_wait ]]; then
                print_status "WARNING" "$service did not become ready within ${max_wait}s"
                break
            fi
        done
    done
    
    return 0
}

# Function to show deployment status
show_status() {
    if [[ "$DRY_RUN" == "true" ]]; then
        print_status "INFO" "Would show deployment status"
        return 0
    fi
    
    print_status "STEP" "Deployment Status"
    
    echo ""
    echo "Services:"
    docker compose --file "$COMPOSE_FILE" ps
    
    echo ""
    echo "Access Information:"
    echo "  Frontend: http://localhost:${FRONTEND_HTTP_PORT:-80}"
    echo "  Backend API: http://localhost:${BACKEND_PORT:-5000}"
    
    if [[ "$ENABLE_MONITORING" == "true" ]]; then
        echo "  Prometheus: http://localhost:${PROMETHEUS_PORT:-9090}"
        echo "  Grafana: http://localhost:${GRAFANA_PORT:-3000}"
    fi
    
    echo ""
    echo "Data Directory: $DATA_DIR"
    echo "Environment File: $ENV_FILE"
    echo "Compose File: $COMPOSE_FILE"
    
    echo ""
    echo "Useful Commands:"
    echo "  View logs: docker compose --file $COMPOSE_FILE logs -f"
    echo "  Stop services: docker compose --file $COMPOSE_FILE down"
    echo "  Update services: docker compose --file $COMPOSE_FILE pull && docker compose --file $COMPOSE_FILE up -d"
    
    return 0
}

# Function to cleanup on error
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        print_status "ERROR" "Deployment failed with exit code $exit_code"
        
        if [[ "$DRY_RUN" == "false" ]]; then
            print_status "INFO" "Check logs with: docker compose --file $COMPOSE_FILE logs"
        fi
    fi
    exit $exit_code
}

# Main function
main() {
    echo "=================================="
    echo "🐳 BDC Docker Portable Deployment"
    echo "=================================="
    echo ""
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    # Parse command line arguments
    parse_args "$@"
    
    # Show configuration
    print_status "INFO" "Deployment Configuration:"
    echo "  Mode: $DEPLOYMENT_MODE"
    echo "  Monitoring: $ENABLE_MONITORING"
    echo "  Skip Build: $SKIP_BUILD"
    echo "  Force Recreate: $FORCE_RECREATE"
    echo "  Dry Run: $DRY_RUN"
    echo "  Project Dir: $PROJECT_DIR"
    echo "  Data Dir: $DATA_DIR"
    echo ""
    
    # Execute deployment steps
    validate_prerequisites
    setup_environment
    setup_data_directories
    build_images
    deploy_services
    wait_for_services
    show_status
    
    echo ""
    print_status "SUCCESS" "BDC deployment completed successfully! 🎉"
    
    if [[ "$DRY_RUN" == "false" ]]; then
        echo ""
        print_status "INFO" "Your BDC application is now running"
        print_status "INFO" "Access it at http://localhost:${FRONTEND_HTTP_PORT:-80}"
    fi
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
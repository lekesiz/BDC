#!/bin/bash
# ================================
# BDC Jaeger Tracing Deployment Script
# ================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
ENV_FILE="${PROJECT_DIR}/.env"
COMPOSE_FILE_MAIN="${PROJECT_DIR}/docker-compose.portable.yml"
COMPOSE_FILE_JAEGER="${PROJECT_DIR}/docker-compose.jaeger.yml"

# Default values
TRACING_PROFILE="tracing"
DRY_RUN=false
WITH_ELK=false
WITH_MONITORING=false
FORCE_RECREATE=false
SKIP_PREREQUISITES=false

# ================================
# Helper Functions
# ================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_usage() {
    cat << EOF
BDC Jaeger Tracing Deployment Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --with-elk          Include ELK stack for log correlation
    --with-monitoring   Include Prometheus/Grafana monitoring
    --dry-run          Show what would be done without executing
    --force-recreate   Force recreation of all containers
    --skip-prerequisites  Skip prerequisites check
    --help             Show this help message

EXAMPLES:
    $0                           # Deploy Jaeger tracing only
    $0 --with-elk --with-monitoring  # Deploy full observability stack
    $0 --dry-run                 # Show what would be deployed
    $0 --force-recreate          # Force recreate all containers

ENVIRONMENT VARIABLES:
    JAEGER_MEMORY_LIMIT         Default: 512M
    JAEGER_CPU_LIMIT           Default: 0.5
    OTEL_MEMORY_LIMIT          Default: 256M
    JAEGER_UI_PORT             Default: 16686
    JAEGER_OTLP_GRPC_PORT      Default: 4317
    JAEGER_OTLP_HTTP_PORT      Default: 4318
    
DATA DIRECTORIES:
    ./data/jaeger              Jaeger storage data
    
ACCESS URLS:
    Jaeger UI:       http://localhost:16686
    OTLP gRPC:       localhost:4317
    OTLP HTTP:       localhost:4318
EOF
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check available memory (minimum 2GB recommended for Jaeger)
    if command -v free &> /dev/null; then
        TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
        if [ "${TOTAL_MEM}" -lt 2000 ]; then
            log_warning "System has less than 2GB RAM. Jaeger may perform poorly."
        fi
    fi
    
    log_success "Prerequisites check completed"
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Check if .env file exists
    if [[ ! -f "${ENV_FILE}" ]]; then
        if [[ -f "${ENV_FILE}.production.template" ]]; then
            log_warning ".env file not found. Creating from template..."
            cp "${ENV_FILE}.production.template" "${ENV_FILE}"
            log_warning "Please edit .env file with your configuration before proceeding"
            exit 1
        else
            log_error ".env file not found and no template available"
            exit 1
        fi
    fi
    
    # Add tracing-specific environment variables if not present
    if ! grep -q "TRACING_ENABLED" "${ENV_FILE}"; then
        echo "" >> "${ENV_FILE}"
        echo "# Distributed Tracing Configuration" >> "${ENV_FILE}"
        echo "TRACING_ENABLED=true" >> "${ENV_FILE}"
        echo "TRACING_SAMPLE_RATE=1.0" >> "${ENV_FILE}"
        echo "BDC_ENVIRONMENT=production" >> "${ENV_FILE}"
        echo "BDC_VERSION=1.0.0" >> "${ENV_FILE}"
        log_info "Added tracing configuration to .env file"
    fi
    
    log_success "Environment setup completed"
}

create_data_directories() {
    log_info "Creating data directories..."
    
    local DATA_DIR="${PROJECT_DIR}/data"
    
    # Create directories
    mkdir -p "${DATA_DIR}/jaeger"
    
    # Set proper permissions
    if [[ "$(uname)" == "Linux" ]]; then
        # Jaeger needs specific user ownership
        sudo chown -R 10001:10001 "${DATA_DIR}/jaeger" 2>/dev/null || {
            log_warning "Could not set Jaeger directory ownership. You may need to run:"
            log_warning "sudo chown -R 10001:10001 ${DATA_DIR}/jaeger"
        }
    fi
    
    log_success "Data directories created"
}

deploy_jaeger_stack() {
    log_info "Deploying Jaeger tracing stack..."
    
    local COMPOSE_FILES="-f ${COMPOSE_FILE_MAIN} -f ${COMPOSE_FILE_JAEGER}"
    local PROFILES="--profile ${TRACING_PROFILE}"
    
    if [[ "${WITH_ELK}" == "true" ]]; then
        if [[ -f "${PROJECT_DIR}/docker-compose.elk.yml" ]]; then
            COMPOSE_FILES="${COMPOSE_FILES} -f ${PROJECT_DIR}/docker-compose.elk.yml"
            PROFILES="${PROFILES} --profile elk"
            log_info "ELK stack will be included for log correlation"
        else
            log_warning "ELK compose file not found, skipping ELK integration"
        fi
    fi
    
    if [[ "${WITH_MONITORING}" == "true" ]]; then
        PROFILES="${PROFILES} --profile monitoring"
        log_info "Monitoring stack will be included"
    fi
    
    local COMPOSE_CMD="docker compose ${COMPOSE_FILES} ${PROFILES}"
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        log_info "DRY RUN - Would execute:"
        echo "${COMPOSE_CMD} up -d"
        return 0
    fi
    
    # Pull images first
    log_info "Pulling Docker images..."
    ${COMPOSE_CMD} pull
    
    # Start services
    if [[ "${FORCE_RECREATE}" == "true" ]]; then
        log_info "Force recreating containers..."
        ${COMPOSE_CMD} up -d --force-recreate
    else
        log_info "Starting services..."
        ${COMPOSE_CMD} up -d
    fi
    
    log_success "Jaeger tracing stack deployment initiated"
}

wait_for_services() {
    if [[ "${DRY_RUN}" == "true" ]]; then
        return 0
    fi
    
    log_info "Waiting for services to become healthy..."
    
    local MAX_WAIT=300  # 5 minutes
    local WAIT_TIME=0
    
    # Wait for Jaeger
    while [[ ${WAIT_TIME} -lt ${MAX_WAIT} ]]; do
        if curl -s http://localhost:16686/api/services >/dev/null 2>&1; then
            log_success "Jaeger UI is healthy"
            break
        fi
        
        sleep 10
        WAIT_TIME=$((WAIT_TIME + 10))
        log_info "Waiting for Jaeger UI... (${WAIT_TIME}s/${MAX_WAIT}s)"
    done
    
    if [[ ${WAIT_TIME} -ge ${MAX_WAIT} ]]; then
        log_error "Jaeger UI did not become healthy within ${MAX_WAIT} seconds"
        return 1
    fi
    
    # Wait for OTLP endpoints
    WAIT_TIME=0
    while [[ ${WAIT_TIME} -lt ${MAX_WAIT} ]]; do
        if nc -z localhost 4317 && nc -z localhost 4318; then
            log_success "OTLP endpoints are healthy"
            break
        fi
        
        sleep 5
        WAIT_TIME=$((WAIT_TIME + 5))
        log_info "Waiting for OTLP endpoints... (${WAIT_TIME}s/${MAX_WAIT}s)"
    done
    
    if [[ ${WAIT_TIME} -ge ${MAX_WAIT} ]]; then
        log_warning "OTLP endpoints did not become healthy within ${MAX_WAIT} seconds"
    fi
}

test_tracing() {
    if [[ "${DRY_RUN}" == "true" ]]; then
        return 0
    fi
    
    log_info "Testing tracing functionality..."
    
    # Test Jaeger API
    if curl -s http://localhost:16686/api/services | jq . >/dev/null 2>&1; then
        log_success "Jaeger API is responding"
    else
        log_warning "Jaeger API test failed"
    fi
    
    # Test OTLP HTTP endpoint
    if curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{"resourceSpans":[]}' \
        http://localhost:4318/v1/traces >/dev/null 2>&1; then
        log_success "OTLP HTTP endpoint is accepting traces"
    else
        log_warning "OTLP HTTP endpoint test failed"
    fi
    
    # Test if backend is sending traces
    sleep 5
    local TRACES=$(curl -s "http://localhost:16686/api/traces?service=bdc-backend&lookback=1h" | jq '.data | length' 2>/dev/null || echo "0")
    if [[ "$TRACES" -gt 0 ]]; then
        log_success "Backend is sending traces to Jaeger"
    else
        log_info "No traces from backend yet (this is normal for new deployments)"
    fi
}

show_status() {
    if [[ "${DRY_RUN}" == "true" ]]; then
        return 0
    fi
    
    log_info "Deployment Status:"
    echo ""
    
    # Show running containers
    docker compose -f "${COMPOSE_FILE_MAIN}" -f "${COMPOSE_FILE_JAEGER}" ps
    
    echo ""
    log_info "Access URLs:"
    echo "  🔍 Jaeger UI:      http://localhost:16686"
    echo "  📡 OTLP gRPC:      localhost:4317"
    echo "  📡 OTLP HTTP:      localhost:4318"
    echo "  📊 Jaeger Metrics: http://localhost:14269/metrics"
    
    if [[ "${WITH_ELK}" == "true" ]]; then
        echo "  📝 Kibana:         http://localhost:5601"
        echo "  🔍 Elasticsearch:  http://localhost:9200"
    fi
    
    if [[ "${WITH_MONITORING}" == "true" ]]; then
        echo "  📈 Grafana:        http://localhost:3000"
        echo "  📊 Prometheus:     http://localhost:9090"
    fi
    
    echo ""
    log_info "Tracing Configuration:"
    echo "  Service Name:      bdc-backend"
    echo "  Sample Rate:       $(grep TRACING_SAMPLE_RATE ${ENV_FILE} | cut -d'=' -f2 || echo '1.0')"
    echo "  Environment:       $(grep BDC_ENVIRONMENT ${ENV_FILE} | cut -d'=' -f2 || echo 'production')"
    
    echo ""
    log_info "Useful Commands:"
    echo "  View traces:       curl 'http://localhost:16686/api/traces?service=bdc-backend'"
    echo "  View services:     curl 'http://localhost:16686/api/services'"
    echo "  Stop tracing:      docker compose -f docker-compose.portable.yml -f docker-compose.jaeger.yml --profile tracing down"
    echo "  View logs:         docker compose -f docker-compose.portable.yml -f docker-compose.jaeger.yml logs -f jaeger"
}

cleanup_on_exit() {
    if [[ $? -ne 0 ]]; then
        log_error "Deployment failed!"
        log_info "Check logs with: docker compose -f docker-compose.portable.yml -f docker-compose.jaeger.yml logs"
    fi
}

# ================================
# Main Function
# ================================

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --with-elk)
                WITH_ELK=true
                shift
                ;;
            --with-monitoring)
                WITH_MONITORING=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --force-recreate)
                FORCE_RECREATE=true
                shift
                ;;
            --skip-prerequisites)
                SKIP_PREREQUISITES=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Set up trap for cleanup
    trap cleanup_on_exit EXIT
    
    # Main deployment flow
    log_info "Starting BDC Jaeger Tracing deployment..."
    
    if [[ "${SKIP_PREREQUISITES}" != "true" ]]; then
        check_prerequisites
    fi
    
    setup_environment
    create_data_directories
    deploy_jaeger_stack
    wait_for_services
    test_tracing
    show_status
    
    log_success "Jaeger Tracing deployment completed successfully!"
    
    if [[ "${DRY_RUN}" != "true" ]]; then
        echo ""
        log_info "Next steps:"
        echo "1. Open Jaeger UI at http://localhost:16686"
        echo "2. Make some API requests to generate traces"
        echo "3. View traces in Jaeger for service 'bdc-backend'"
        echo "4. Check trace correlation with logs in Kibana (if ELK enabled)"
        echo "5. Monitor trace metrics in Grafana (if monitoring enabled)"
    fi
}

# ================================
# Script Execution
# ================================

main "$@"
#!/bin/bash
# ================================
# BDC ELK Stack Deployment Script
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
COMPOSE_FILE_ELK="${PROJECT_DIR}/docker-compose.elk.yml"

# Default values
ELK_PROFILE="elk"
DRY_RUN=false
MONITORING_ENABLED=false
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
BDC ELK Stack Deployment Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --monitoring        Enable Prometheus/Grafana monitoring alongside ELK
    --dry-run          Show what would be done without executing
    --force-recreate   Force recreation of all containers
    --skip-prerequisites  Skip prerequisites check
    --help             Show this help message

EXAMPLES:
    $0                           # Deploy ELK stack only
    $0 --monitoring              # Deploy ELK + Prometheus/Grafana
    $0 --dry-run --monitoring    # Show what would be deployed
    $0 --force-recreate          # Force recreate all containers

ENVIRONMENT VARIABLES:
    ELK_ELASTICSEARCH_MEMORY     Default: 1G
    ELK_LOGSTASH_MEMORY         Default: 1G
    ELK_KIBANA_MEMORY           Default: 512M
    ELK_FILEBEAT_MEMORY         Default: 256M
    ELK_METRICBEAT_MEMORY       Default: 256M
    KIBANA_ENCRYPTION_KEY       Default: auto-generated
    
DATA DIRECTORIES:
    ./data/elasticsearch        Elasticsearch data
    ./data/kibana              Kibana data
    ./data/logs                Application logs
    
ACCESS URLS:
    Kibana:      http://localhost:5601
    Elasticsearch: http://localhost:9200
    Logstash:    http://localhost:9600
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
    
    # Check available memory (minimum 4GB recommended for ELK)
    if command -v free &> /dev/null; then
        TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
        if [ "${TOTAL_MEM}" -lt 4000 ]; then
            log_warning "System has less than 4GB RAM. ELK stack may perform poorly."
            log_warning "Consider increasing vm.max_map_count for Elasticsearch:"
            log_warning "sudo sysctl -w vm.max_map_count=262144"
        fi
    fi
    
    # Check vm.max_map_count for Elasticsearch
    if [[ "$(uname)" == "Linux" ]]; then
        MAX_MAP_COUNT=$(sysctl vm.max_map_count | cut -d' ' -f3)
        if [ "${MAX_MAP_COUNT}" -lt 262144 ]; then
            log_warning "vm.max_map_count is too low for Elasticsearch"
            log_warning "Run: sudo sysctl -w vm.max_map_count=262144"
            log_warning "To make permanent: echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf"
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
    
    # Generate Kibana encryption key if not set
    if ! grep -q "KIBANA_ENCRYPTION_KEY" "${ENV_FILE}" || grep -q "your-32-character-secret-key-here" "${ENV_FILE}"; then
        KIBANA_KEY=$(openssl rand -hex 16)
        if grep -q "KIBANA_ENCRYPTION_KEY" "${ENV_FILE}"; then
            sed -i.bak "s/KIBANA_ENCRYPTION_KEY=.*/KIBANA_ENCRYPTION_KEY=${KIBANA_KEY}/" "${ENV_FILE}"
        else
            echo "KIBANA_ENCRYPTION_KEY=${KIBANA_KEY}" >> "${ENV_FILE}"
        fi
        log_info "Generated Kibana encryption key"
    fi
    
    log_success "Environment setup completed"
}

create_data_directories() {
    log_info "Creating data directories..."
    
    local DATA_DIR="${PROJECT_DIR}/data"
    
    # Create directories
    mkdir -p "${DATA_DIR}"/{elasticsearch,kibana,logs}
    
    # Set proper permissions for Elasticsearch
    if [[ "$(uname)" == "Linux" ]]; then
        # Elasticsearch needs specific user ownership
        sudo chown -R 1000:1000 "${DATA_DIR}/elasticsearch" 2>/dev/null || {
            log_warning "Could not set Elasticsearch directory ownership. You may need to run:"
            log_warning "sudo chown -R 1000:1000 ${DATA_DIR}/elasticsearch"
        }
    fi
    
    log_success "Data directories created"
}

deploy_elk_stack() {
    log_info "Deploying ELK stack..."
    
    local COMPOSE_FILES="-f ${COMPOSE_FILE_MAIN} -f ${COMPOSE_FILE_ELK}"
    local PROFILES="--profile ${ELK_PROFILE}"
    
    if [[ "${MONITORING_ENABLED}" == "true" ]]; then
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
    
    log_success "ELK stack deployment initiated"
}

wait_for_services() {
    if [[ "${DRY_RUN}" == "true" ]]; then
        return 0
    fi
    
    log_info "Waiting for services to become healthy..."
    
    local MAX_WAIT=300  # 5 minutes
    local WAIT_TIME=0
    
    while [[ ${WAIT_TIME} -lt ${MAX_WAIT} ]]; do
        # Check Elasticsearch
        if curl -s http://localhost:9200/_cluster/health >/dev/null 2>&1; then
            log_success "Elasticsearch is healthy"
            break
        fi
        
        sleep 10
        WAIT_TIME=$((WAIT_TIME + 10))
        log_info "Waiting for Elasticsearch... (${WAIT_TIME}s/${MAX_WAIT}s)"
    done
    
    if [[ ${WAIT_TIME} -ge ${MAX_WAIT} ]]; then
        log_error "Elasticsearch did not become healthy within ${MAX_WAIT} seconds"
        return 1
    fi
    
    # Wait for Kibana
    WAIT_TIME=0
    while [[ ${WAIT_TIME} -lt ${MAX_WAIT} ]]; do
        if curl -s http://localhost:5601/api/status >/dev/null 2>&1; then
            log_success "Kibana is healthy"
            break
        fi
        
        sleep 10
        WAIT_TIME=$((WAIT_TIME + 10))
        log_info "Waiting for Kibana... (${WAIT_TIME}s/${MAX_WAIT}s)"
    done
    
    if [[ ${WAIT_TIME} -ge ${MAX_WAIT} ]]; then
        log_warning "Kibana did not become healthy within ${MAX_WAIT} seconds"
    fi
}

show_status() {
    if [[ "${DRY_RUN}" == "true" ]]; then
        return 0
    fi
    
    log_info "Deployment Status:"
    echo ""
    
    # Show running containers
    docker compose -f "${COMPOSE_FILE_MAIN}" -f "${COMPOSE_FILE_ELK}" ps
    
    echo ""
    log_info "Access URLs:"
    echo "  📊 Kibana:         http://localhost:5601"
    echo "  🔍 Elasticsearch:  http://localhost:9200"
    echo "  🔄 Logstash:       http://localhost:9600"
    
    if [[ "${MONITORING_ENABLED}" == "true" ]]; then
        echo "  📈 Grafana:        http://localhost:3000"
        echo "  📊 Prometheus:     http://localhost:9090"
    fi
    
    echo ""
    log_info "Index Patterns (to configure in Kibana):"
    echo "  📝 Application:    filebeat-bdc-*"
    echo "  📊 Metrics:        metricbeat-bdc-*"
    echo "  🔄 Logstash:       bdc-*"
    
    echo ""
    log_info "Useful Commands:"
    echo "  View logs:    docker compose -f docker-compose.portable.yml -f docker-compose.elk.yml logs -f"
    echo "  Stop stack:   docker compose -f docker-compose.portable.yml -f docker-compose.elk.yml --profile elk down"
    echo "  Restart:      $0 --force-recreate"
}

cleanup_on_exit() {
    if [[ $? -ne 0 ]]; then
        log_error "Deployment failed!"
        log_info "Check logs with: docker compose -f docker-compose.portable.yml -f docker-compose.elk.yml logs"
    fi
}

# ================================
# Main Function
# ================================

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --monitoring)
                MONITORING_ENABLED=true
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
    log_info "Starting BDC ELK Stack deployment..."
    
    if [[ "${SKIP_PREREQUISITES}" != "true" ]]; then
        check_prerequisites
    fi
    
    setup_environment
    create_data_directories
    deploy_elk_stack
    wait_for_services
    show_status
    
    log_success "ELK Stack deployment completed successfully!"
    
    if [[ "${DRY_RUN}" != "true" ]]; then
        echo ""
        log_info "Next steps:"
        echo "1. Open Kibana at http://localhost:5601"
        echo "2. Configure index patterns: filebeat-bdc-*, metricbeat-bdc-*"
        echo "3. Import dashboards and visualizations"
        echo "4. Set up alerts and notifications"
    fi
}

# ================================
# Script Execution
# ================================

main "$@"
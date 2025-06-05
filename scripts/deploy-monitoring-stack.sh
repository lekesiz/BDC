#!/bin/bash

# BDC Monitoring Stack Deployment Script
# Deploys comprehensive monitoring with Prometheus, Grafana, AlertManager, and more

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🚀 BDC Monitoring Stack Deployment${NC}"
echo "========================================"

# Function to print status messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker status..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    print_status "Docker is running ✓"
}

# Check if environment file exists
check_environment() {
    print_status "Checking environment configuration..."
    
    if [[ ! -f "$PROJECT_ROOT/.env.production" ]]; then
        if [[ -f "$PROJECT_ROOT/.env.production.template" ]]; then
            print_warning ".env.production not found. Copying from template..."
            cp "$PROJECT_ROOT/.env.production.template" "$PROJECT_ROOT/.env.production"
            print_warning "Please configure the monitoring variables in .env.production"
        else
            print_error ".env.production.template not found!"
            exit 1
        fi
    fi
    
    print_status "Environment configuration found ✓"
}

# Create necessary directories
create_directories() {
    print_status "Creating monitoring directories..."
    
    mkdir -p "$PROJECT_ROOT/data/prometheus"
    mkdir -p "$PROJECT_ROOT/data/grafana"
    mkdir -p "$PROJECT_ROOT/data/alertmanager"
    mkdir -p "$PROJECT_ROOT/data/loki"
    
    # Set proper permissions
    chmod 777 "$PROJECT_ROOT/data/prometheus"
    chmod 777 "$PROJECT_ROOT/data/grafana" 
    chmod 777 "$PROJECT_ROOT/data/alertmanager"
    chmod 777 "$PROJECT_ROOT/data/loki"
    
    print_status "Directories created ✓"
}

# Validate configuration files
validate_configs() {
    print_status "Validating configuration files..."
    
    local configs=(
        "$PROJECT_ROOT/monitoring/prometheus/prometheus.yml"
        "$PROJECT_ROOT/monitoring/grafana/provisioning/datasources/datasources.yaml"
        "$PROJECT_ROOT/monitoring/alertmanager/alertmanager.yml"
    )
    
    for config in "${configs[@]}"; do
        if [[ ! -f "$config" ]]; then
            print_error "Configuration file not found: $config"
            exit 1
        fi
    done
    
    print_status "Configuration files validated ✓"
}

# Build custom images if needed
build_images() {
    print_status "Building custom images..."
    
    # Build backend image with metrics exporter
    if [[ -f "$PROJECT_ROOT/server/Dockerfile" ]]; then
        docker build -t bdc-backend:latest "$PROJECT_ROOT/server/"
        print_status "Backend image built ✓"
    else
        print_warning "Backend Dockerfile not found, skipping custom backend build"
    fi
}

# Deploy monitoring stack
deploy_monitoring() {
    print_status "Deploying monitoring stack..."
    
    cd "$PROJECT_ROOT"
    
    # Create network if it doesn't exist
    docker network create bdc-network 2>/dev/null || true
    
    # Deploy monitoring services
    docker-compose -f docker-compose.monitoring.yml up -d
    
    print_status "Monitoring stack deployed ✓"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    local services=(
        "prometheus:9090"
        "grafana:3000"
        "alertmanager:9093"
        "node-exporter:9100"
        "cadvisor:8080"
    )
    
    local max_attempts=30
    local attempt=0
    
    for service in "${services[@]}"; do
        local host=$(echo "$service" | cut -d: -f1)
        local port=$(echo "$service" | cut -d: -f2)
        
        attempt=0
        while [[ $attempt -lt $max_attempts ]]; do
            if curl -f "http://localhost:$port" > /dev/null 2>&1; then
                print_status "$host is healthy ✓"
                break
            fi
            
            attempt=$((attempt + 1))
            if [[ $attempt -eq $max_attempts ]]; then
                print_warning "$host is not responding after $max_attempts attempts"
            else
                sleep 10
            fi
        done
    done
}

# Display access information
show_access_info() {
    print_status "Monitoring Stack Access Information:"
    echo ""
    echo -e "${BLUE}📊 Prometheus:${NC} http://localhost:9090"
    echo -e "${BLUE}📈 Grafana:${NC} http://localhost:3000 (admin/admin)"
    echo -e "${BLUE}🚨 AlertManager:${NC} http://localhost:9093"
    echo -e "${BLUE}💻 Node Exporter:${NC} http://localhost:9100"
    echo -e "${BLUE}🐳 cAdvisor:${NC} http://localhost:8080"
    echo -e "${BLUE}📊 App Metrics:${NC} http://localhost:8000/metrics"
    echo -e "${BLUE}📊 Blackbox Exporter:${NC} http://localhost:9115"
    echo -e "${BLUE}📝 Loki:${NC} http://localhost:3100"
    echo ""
    echo -e "${YELLOW}💡 Tip:${NC} Change the default Grafana password after first login!"
    echo -e "${YELLOW}💡 Tip:${NC} Import the BDC dashboard from the provisioned dashboards"
    echo ""
}

# Setup initial Grafana dashboards
setup_grafana() {
    print_status "Setting up Grafana dashboards..."
    
    # Wait for Grafana to be ready
    local attempt=0
    local max_attempts=20
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
            break
        fi
        attempt=$((attempt + 1))
        sleep 5
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        print_warning "Grafana is not ready, skipping dashboard setup"
        return
    fi
    
    print_status "Grafana is ready, dashboards will be auto-provisioned ✓"
}

# Test monitoring setup
test_monitoring() {
    print_status "Testing monitoring setup..."
    
    # Test Prometheus targets
    local prom_targets=$(curl -s http://localhost:9090/api/v1/targets | grep -o '"health":"up"' | wc -l)
    print_status "Prometheus has $prom_targets healthy targets"
    
    # Test metrics collection
    if curl -f http://localhost:8000/metrics > /dev/null 2>&1; then
        print_status "Application metrics are being collected ✓"
    else
        print_warning "Application metrics endpoint is not responding"
    fi
    
    # Test alerting rules
    local alert_rules=$(curl -s http://localhost:9090/api/v1/rules | grep -o '"alerts":\[' | wc -l)
    print_status "Prometheus has $alert_rules alert rule groups loaded"
    
    print_status "Monitoring setup test completed ✓"
}

# Show logs for troubleshooting
show_logs() {
    if [[ "${1:-}" == "--logs" ]]; then
        print_status "Showing monitoring stack logs..."
        docker-compose -f "$PROJECT_ROOT/docker-compose.monitoring.yml" logs --tail=50
    fi
}

# Main deployment function
main() {
    echo -e "${BLUE}Starting BDC Monitoring Stack Deployment...${NC}"
    echo ""
    
    check_docker
    check_environment
    create_directories
    validate_configs
    build_images
    deploy_monitoring
    wait_for_services
    setup_grafana
    test_monitoring
    
    echo ""
    echo -e "${GREEN}🎉 Monitoring Stack Deployment Complete!${NC}"
    echo ""
    
    show_access_info
    show_logs "$@"
}

# Handle script arguments
case "${1:-}" in
    --logs)
        main --logs
        ;;
    --help)
        echo "BDC Monitoring Stack Deployment Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --logs    Show service logs after deployment"
        echo "  --help    Show this help message"
        echo ""
        ;;
    *)
        main
        ;;
esac
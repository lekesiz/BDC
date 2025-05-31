#!/bin/bash
# SSL/TLS certificate setup script for BDC production

set -e

# Configuration
DOMAIN=${1:-yourdomain.com}
EMAIL=${2:-admin@yourdomain.com}
CERT_DIR="/etc/ssl/bdc"
NGINX_CONF_DIR="/etc/nginx"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Please run as root"
        exit 1
    fi
}

# Install Certbot
install_certbot() {
    log_info "Installing Certbot..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        apt-get update
        apt-get install -y certbot python3-certbot-nginx
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        yum install -y epel-release
        yum install -y certbot python3-certbot-nginx
    elif command -v dnf &> /dev/null; then
        # Fedora
        dnf install -y certbot python3-certbot-nginx
    else
        log_error "Unsupported package manager"
        exit 1
    fi
}

# Generate self-signed certificate for testing
generate_self_signed() {
    log_info "Generating self-signed certificate for $DOMAIN..."
    
    mkdir -p $CERT_DIR
    
    # Generate private key
    openssl genrsa -out $CERT_DIR/key.pem 4096
    
    # Generate certificate signing request
    openssl req -new -key $CERT_DIR/key.pem -out $CERT_DIR/csr.pem -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
    
    # Generate self-signed certificate
    openssl x509 -req -in $CERT_DIR/csr.pem -signkey $CERT_DIR/key.pem -out $CERT_DIR/cert.pem -days 365
    
    # Set permissions
    chmod 600 $CERT_DIR/key.pem
    chmod 644 $CERT_DIR/cert.pem
    
    log_info "Self-signed certificate generated at $CERT_DIR/"
}

# Obtain Let's Encrypt certificate
obtain_letsencrypt() {
    log_info "Obtaining Let's Encrypt certificate for $DOMAIN..."
    
    # Stop nginx temporarily
    systemctl stop nginx || true
    
    # Obtain certificate
    certbot certonly --standalone \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN \
        -d www.$DOMAIN
    
    # Copy certificates to our directory
    mkdir -p $CERT_DIR
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $CERT_DIR/cert.pem
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $CERT_DIR/key.pem
    
    # Set permissions
    chmod 600 $CERT_DIR/key.pem
    chmod 644 $CERT_DIR/cert.pem
    
    log_info "Let's Encrypt certificate obtained"
}

# Setup automatic renewal
setup_renewal() {
    log_info "Setting up automatic certificate renewal..."
    
    # Create renewal script
    cat > /usr/local/bin/renew-bdc-cert.sh << 'EOF'
#!/bin/bash
certbot renew --quiet --post-hook "systemctl reload nginx"
EOF
    
    chmod +x /usr/local/bin/renew-bdc-cert.sh
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/renew-bdc-cert.sh") | crontab -
    
    log_info "Automatic renewal configured"
}

# Configure SSL security
configure_ssl_security() {
    log_info "Configuring SSL security settings..."
    
    # Generate DH parameters
    openssl dhparam -out $CERT_DIR/dhparam.pem 2048
    
    # Create SSL configuration snippet
    cat > $NGINX_CONF_DIR/snippets/ssl-bdc.conf << EOF
ssl_certificate $CERT_DIR/cert.pem;
ssl_certificate_key $CERT_DIR/key.pem;

# SSL Security
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
ssl_prefer_server_ciphers off;

# SSL Session
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_session_tickets off;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# DH Parameters
ssl_dhparam $CERT_DIR/dhparam.pem;

# Security Headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
EOF
    
    log_info "SSL security configured"
}

# Test SSL configuration
test_ssl() {
    log_info "Testing SSL configuration..."
    
    # Test nginx configuration
    nginx -t
    
    if [ $? -eq 0 ]; then
        log_info "Nginx configuration test passed"
    else
        log_error "Nginx configuration test failed"
        exit 1
    fi
    
    # Restart nginx
    systemctl restart nginx
    
    # Test SSL certificate
    echo | openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | openssl x509 -noout -dates
    
    log_info "SSL test completed"
}

# Main function
main() {
    check_root
    
    case "${3:-letsencrypt}" in
        "self-signed")
            generate_self_signed
            ;;
        "letsencrypt")
            install_certbot
            obtain_letsencrypt
            setup_renewal
            ;;
        *)
            log_error "Unknown certificate type. Use 'self-signed' or 'letsencrypt'"
            exit 1
            ;;
    esac
    
    configure_ssl_security
    test_ssl
    
    log_info "SSL setup completed successfully!"
    log_info "Certificate location: $CERT_DIR/"
    log_info "Nginx SSL config: $NGINX_CONF_DIR/snippets/ssl-bdc.conf"
}

# Show usage
usage() {
    echo "Usage: $0 <domain> <email> [letsencrypt|self-signed]"
    echo "Example: $0 yourdomain.com admin@yourdomain.com letsencrypt"
    exit 1
}

# Check arguments
if [ $# -lt 2 ]; then
    usage
fi

main "$@"
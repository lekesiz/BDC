#!/bin/bash

# ClamAV setup script for different environments

set -e

echo "🦠 Setting up ClamAV virus scanner..."

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v apt-get >/dev/null 2>&1; then
        # Debian/Ubuntu
        echo "📦 Installing ClamAV on Debian/Ubuntu..."
        sudo apt-get update
        sudo apt-get install -y clamav clamav-daemon clamav-freshclam
        
        # Stop services for configuration
        sudo systemctl stop clamav-freshclam
        sudo systemctl stop clamav-daemon
        
        # Update virus database
        echo "🔄 Updating virus database..."
        sudo freshclam
        
        # Start services
        sudo systemctl start clamav-freshclam
        sudo systemctl start clamav-daemon
        sudo systemctl enable clamav-freshclam
        sudo systemctl enable clamav-daemon
        
    elif command -v yum >/dev/null 2>&1; then
        # RHEL/CentOS
        echo "📦 Installing ClamAV on RHEL/CentOS..."
        sudo yum install -y epel-release
        sudo yum install -y clamav clamav-update clamd
        
        # Configure SELinux
        sudo setsebool -P antivirus_can_scan_system 1
        sudo setsebool -P clamd_use_jit 1
        
        # Update virus database
        echo "🔄 Updating virus database..."
        sudo freshclam
        
        # Start services
        sudo systemctl start clamd@scan
        sudo systemctl enable clamd@scan
    fi
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew >/dev/null 2>&1; then
        echo "📦 Installing ClamAV on macOS..."
        brew install clamav
        
        # Create config files
        cp /opt/homebrew/etc/clamav/freshclam.conf.sample /opt/homebrew/etc/clamav/freshclam.conf
        cp /opt/homebrew/etc/clamav/clamd.conf.sample /opt/homebrew/etc/clamav/clamd.conf
        
        # Edit config files
        sed -i '' 's/^Example/#Example/' /opt/homebrew/etc/clamav/freshclam.conf
        sed -i '' 's/^Example/#Example/' /opt/homebrew/etc/clamav/clamd.conf
        
        # Update virus database
        echo "🔄 Updating virus database..."
        freshclam
        
        # Start daemon
        brew services start clamav
    else
        echo "❌ Homebrew not found. Please install Homebrew first."
        exit 1
    fi
fi

# Docker setup
if command -v docker >/dev/null 2>&1; then
    echo "🐳 Creating Docker Compose service for ClamAV..."
    
    cat > docker-compose.clamav.yml << 'EOF'
version: '3.8'

services:
  clamav:
    image: clamav/clamav:latest
    container_name: bdc_clamav
    restart: unless-stopped
    ports:
      - "3310:3310"
    volumes:
      - clamav_db:/var/lib/clamav
      - ./quarantine:/quarantine
    environment:
      - CLAMAV_NO_CLAMD=false
      - CLAMAV_NO_FRESHCLAMD=false
      - CLAMAV_NO_MILTERD=true
    networks:
      - bdc_network
    healthcheck:
      test: ["CMD", "clamdscan", "--version"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  clamav_db:

networks:
  bdc_network:
    external: true
EOF

    echo "✅ Docker Compose file created: docker-compose.clamav.yml"
    echo "To start ClamAV in Docker: docker-compose -f docker-compose.clamav.yml up -d"
fi

# Test installation
echo "🧪 Testing ClamAV installation..."
if command -v clamscan >/dev/null 2>&1; then
    clamscan --version
    echo "✅ ClamAV installed successfully!"
else
    echo "⚠️  ClamAV command-line scanner not found in PATH"
fi

if command -v clamdscan >/dev/null 2>&1; then
    echo "✅ ClamAV daemon scanner available"
else
    echo "⚠️  ClamAV daemon scanner not found"
fi

echo "
📝 Configuration notes:
1. Virus database will be updated automatically
2. For production, configure clamd.conf for your needs
3. Default quarantine path: /tmp/quarantine
4. Make sure your app has permissions to access ClamAV socket

🔧 Environment variables for your app:
ENABLE_CLAMAV=true
CLAMAV_HOST=localhost  # or 'clamav' for Docker
CLAMAV_PORT=3310

Done! 🎉
"
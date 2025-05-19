# BDC Disaster Recovery Plan

## Overview
This document outlines the disaster recovery procedures for the BDC application to ensure business continuity in case of system failures, data loss, or catastrophic events.

## Recovery Objectives

### RTO (Recovery Time Objective)
- **Critical Systems**: 2 hours
- **Non-critical Systems**: 8 hours
- **Full Recovery**: 24 hours

### RPO (Recovery Point Objective)
- **Database**: 1 hour (maximum data loss)
- **File Storage**: 24 hours
- **Configuration**: Real-time (version control)

## Disaster Scenarios

### 1. Server Hardware Failure
**Impact**: Complete system unavailability
**Recovery Strategy**: Failover to standby server or cloud deployment

### 2. Database Corruption
**Impact**: Data integrity issues, potential data loss
**Recovery Strategy**: Restore from recent backup

### 3. Cyber Attack
**Impact**: Data breach, system compromise
**Recovery Strategy**: Isolate, analyze, restore from clean backup

### 4. Natural Disaster
**Impact**: Data center unavailability
**Recovery Strategy**: Activate off-site disaster recovery site

### 5. Human Error
**Impact**: Accidental data deletion or misconfiguration
**Recovery Strategy**: Restore from backups or version control

## Backup Strategy

### Database Backups
```bash
#!/bin/bash
# Automated PostgreSQL backup script
BACKUP_DIR="/var/backups/bdc/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="bdc_production"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
pg_dump -U postgres -h localhost $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Copy to off-site storage
aws s3 cp $BACKUP_DIR/db_backup_$DATE.sql.gz s3://bdc-backups/postgres/

# Remove local backups older than 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

# Verify backup
if [ -f $BACKUP_DIR/db_backup_$DATE.sql.gz ]; then
    echo "Backup successful: db_backup_$DATE.sql.gz"
else
    echo "Backup failed!" | mail -s "BDC Backup Failure" admin@company.com
fi
```

### Application Backups
```bash
#!/bin/bash
# Application files backup
BACKUP_DIR="/var/backups/bdc/application"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/var/www/bdc"

# Create backup
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz -C $APP_DIR .

# Upload to S3
aws s3 cp $BACKUP_DIR/app_backup_$DATE.tar.gz s3://bdc-backups/application/

# Keep only last 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Incremental Backups
```bash
#!/bin/bash
# Incremental backup using rsync
BACKUP_DIR="/var/backups/bdc/incremental"
SOURCE_DIR="/var/www/bdc"
REMOTE_HOST="backup.server.com"

# Perform incremental backup
rsync -avz --delete \
    --backup --backup-dir=$BACKUP_DIR/$(date +%Y%m%d) \
    $SOURCE_DIR/ $REMOTE_HOST:$BACKUP_DIR/current/

# Rotate old incremental backups
ssh $REMOTE_HOST "find $BACKUP_DIR -type d -mtime +30 -exec rm -rf {} \;"
```

## Recovery Procedures

### 1. Database Recovery
```bash
#!/bin/bash
# Database recovery script
BACKUP_FILE=$1
DB_NAME="bdc_production"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore_db.sh <backup_file>"
    exit 1
fi

# Stop application
sudo systemctl stop bdc

# Drop existing database
sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"

# Restore from backup
gunzip -c $BACKUP_FILE | sudo -u postgres psql $DB_NAME

# Verify restoration
if [ $? -eq 0 ]; then
    echo "Database restored successfully"
    sudo systemctl start bdc
else
    echo "Database restoration failed!"
    exit 1
fi
```

### 2. Application Recovery
```bash
#!/bin/bash
# Application recovery script
BACKUP_FILE=$1
APP_DIR="/var/www/bdc"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore_app.sh <backup_file>"
    exit 1
fi

# Stop services
sudo systemctl stop bdc
sudo systemctl stop nginx

# Backup current state
mv $APP_DIR ${APP_DIR}_backup_$(date +%Y%m%d_%H%M%S)

# Extract backup
mkdir -p $APP_DIR
tar -xzf $BACKUP_FILE -C $APP_DIR

# Set permissions
sudo chown -R www-data:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR

# Restart services
sudo systemctl start bdc
sudo systemctl start nginx

echo "Application restored successfully"
```

### 3. Full System Recovery
```bash
#!/bin/bash
# Full system recovery orchestration
set -e

echo "Starting full system recovery..."

# 1. Restore database
./restore_db.sh /path/to/db_backup.sql.gz

# 2. Restore application files
./restore_app.sh /path/to/app_backup.tar.gz

# 3. Restore configuration
cd /etc
git pull origin main

# 4. Restore SSL certificates
cp /backup/ssl/* /etc/letsencrypt/live/yourdomain.com/

# 5. Restore Redis data
cp /backup/redis/dump.rdb /var/lib/redis/

# 6. Restart all services
sudo systemctl restart postgresql
sudo systemctl restart redis
sudo systemctl restart bdc
sudo systemctl restart nginx

# 7. Verify services
for service in postgresql redis bdc nginx; do
    if systemctl is-active --quiet $service; then
        echo "$service is running"
    else
        echo "ERROR: $service is not running"
        exit 1
    fi
done

echo "Full system recovery completed"
```

## Failover Procedures

### 1. Database Failover
```python
# database_failover.py
import psycopg2
import time
import logging

class DatabaseFailover:
    def __init__(self):
        self.primary_host = "primary.db.server"
        self.standby_host = "standby.db.server"
        self.current_host = self.primary_host
    
    def check_primary_health(self):
        """Check if primary database is healthy"""
        try:
            conn = psycopg2.connect(
                host=self.primary_host,
                database="bdc_production",
                user="bdc_user",
                password="password",
                connect_timeout=5
            )
            conn.close()
            return True
        except:
            return False
    
    def promote_standby(self):
        """Promote standby to primary"""
        logging.info("Promoting standby database")
        # Execute promotion command on standby
        os.system(f"ssh {self.standby_host} 'sudo -u postgres pg_ctl promote'")
        time.sleep(10)  # Wait for promotion
        
        # Update application configuration
        self.update_app_config(self.standby_host)
        self.current_host = self.standby_host
    
    def update_app_config(self, new_host):
        """Update application to use new database host"""
        config_file = "/var/www/bdc/server/.env"
        with open(config_file, 'r') as f:
            content = f.read()
        
        content = content.replace(
            f"DATABASE_HOST={self.current_host}",
            f"DATABASE_HOST={new_host}"
        )
        
        with open(config_file, 'w') as f:
            f.write(content)
        
        # Restart application
        os.system("sudo systemctl restart bdc")
    
    def monitor_and_failover(self):
        """Continuous monitoring and automatic failover"""
        while True:
            if not self.check_primary_health():
                logging.error("Primary database is down!")
                self.promote_standby()
                # Send alerts
                self.send_alert("Database failover completed")
            time.sleep(30)  # Check every 30 seconds
```

### 2. Application Server Failover
```nginx
# /etc/nginx/sites-available/bdc-failover
upstream bdc_servers {
    server app1.server.com:5000 max_fails=3 fail_timeout=30s;
    server app2.server.com:5000 backup;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://bdc_servers;
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Health check
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
}
```

### 3. DNS Failover
```python
# dns_failover.py
import requests
import json

class DNSFailover:
    def __init__(self):
        self.cloudflare_api = "https://api.cloudflare.com/client/v4"
        self.api_token = "your_cloudflare_api_token"
        self.zone_id = "your_zone_id"
        self.record_id = "your_record_id"
    
    def update_dns_record(self, new_ip):
        """Update DNS record to point to new IP"""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "type": "A",
            "name": "yourdomain.com",
            "content": new_ip,
            "ttl": 120,  # Low TTL for quick propagation
            "proxied": True
        }
        
        response = requests.put(
            f"{self.cloudflare_api}/zones/{self.zone_id}/dns_records/{self.record_id}",
            headers=headers,
            data=json.dumps(data)
        )
        
        if response.status_code == 200:
            logging.info(f"DNS updated to {new_ip}")
        else:
            logging.error(f"DNS update failed: {response.text}")
```

## Disaster Recovery Testing

### 1. Monthly DR Drill
```bash
#!/bin/bash
# DR drill script
echo "Starting monthly DR drill..."

# 1. Create test database
sudo -u postgres createdb bdc_dr_test

# 2. Restore backup to test database
latest_backup=$(ls -t /var/backups/bdc/postgres/*.sql.gz | head -1)
gunzip -c $latest_backup | sudo -u postgres psql bdc_dr_test

# 3. Verify data integrity
row_count=$(sudo -u postgres psql -t -c "SELECT COUNT(*) FROM users;" bdc_dr_test)
echo "Restored $row_count users"

# 4. Test application with restored database
export DATABASE_URL="postgresql://postgres@localhost/bdc_dr_test"
python /var/www/bdc/server/test_dr.py

# 5. Clean up
sudo -u postgres dropdb bdc_dr_test

echo "DR drill completed successfully"
```

### 2. Failover Testing
```python
# test_failover.py
import unittest
import time
from disaster_recovery import DatabaseFailover, ApplicationFailover

class TestDisasterRecovery(unittest.TestCase):
    def test_database_failover(self):
        """Test database failover procedure"""
        failover = DatabaseFailover()
        
        # Simulate primary failure
        original_primary = failover.primary_host
        failover.primary_host = "non.existent.host"
        
        # Trigger failover
        failover.promote_standby()
        
        # Verify failover
        self.assertEqual(failover.current_host, failover.standby_host)
        self.assertTrue(failover.check_primary_health())
    
    def test_application_recovery_time(self):
        """Test application recovery meets RTO"""
        start_time = time.time()
        
        # Simulate recovery
        os.system("./restore_app.sh test_backup.tar.gz")
        
        recovery_time = time.time() - start_time
        
        # Verify RTO (2 hours = 7200 seconds)
        self.assertLess(recovery_time, 7200)
```

## Communication Plan

### Incident Response Team
| Role | Name | Contact | Backup |
|------|------|---------|--------|
| Incident Commander | John Doe | +1-xxx-xxx-xxxx | Jane Smith |
| Technical Lead | Bob Johnson | +1-xxx-xxx-xxxx | Alice Brown |
| Database Admin | Charlie Wilson | +1-xxx-xxx-xxxx | David Lee |
| Security Officer | Eve Davis | +1-xxx-xxx-xxxx | Frank Miller |

### Communication Channels
1. **Primary**: Slack (#incident-response)
2. **Secondary**: Email (incident@company.com)
3. **Emergency**: Phone tree
4. **Status Page**: status.yourdomain.com

### Notification Templates
```python
# notification_templates.py
class DisasterNotifications:
    @staticmethod
    def initial_alert(incident_type, severity):
        return f"""
        INCIDENT ALERT - {severity}
        
        Type: {incident_type}
        Time: {datetime.now()}
        Status: Investigating
        
        Initial Response Team has been notified.
        Updates will follow every 15 minutes.
        """
    
    @staticmethod
    def recovery_complete(incident_type, downtime):
        return f"""
        INCIDENT RESOLVED
        
        Type: {incident_type}
        Duration: {downtime}
        Status: Resolved
        
        All systems have been restored to normal operation.
        Post-mortem will be conducted within 48 hours.
        """
```

## Recovery Checklist

### Phase 1: Assessment (0-30 minutes)
- [ ] Identify the type and scope of disaster
- [ ] Activate incident response team
- [ ] Assess impact on users and business
- [ ] Determine recovery strategy
- [ ] Initiate communication plan

### Phase 2: Isolation (30-60 minutes)
- [ ] Isolate affected systems
- [ ] Prevent further damage
- [ ] Preserve evidence for analysis
- [ ] Redirect traffic if necessary
- [ ] Update status page

### Phase 3: Recovery (1-4 hours)
- [ ] Execute recovery procedures
- [ ] Restore from backups
- [ ] Verify data integrity
- [ ] Test system functionality
- [ ] Monitor for stability

### Phase 4: Validation (4-8 hours)
- [ ] Perform comprehensive testing
- [ ] Verify all services are operational
- [ ] Check performance metrics
- [ ] Confirm security measures
- [ ] Get user confirmation

### Phase 5: Post-Recovery (8-24 hours)
- [ ] Document timeline and actions
- [ ] Analyze root cause
- [ ] Update disaster recovery plan
- [ ] Schedule post-mortem meeting
- [ ] Implement preventive measures

## Lessons Learned Repository

### Incident: Database Corruption (Example)
**Date**: 2024-03-15
**Duration**: 4 hours
**Root Cause**: Disk failure during write operation
**Resolution**: Restored from backup, replaced faulty disk
**Improvements**:
- Implemented RAID configuration
- Increased backup frequency
- Added disk health monitoring

### Best Practices
1. **Regular Testing**: Monthly DR drills
2. **Documentation**: Keep procedures updated
3. **Automation**: Automate recovery where possible
4. **Training**: Regular team training sessions
5. **Communication**: Clear escalation paths

## Recovery Metrics

### Key Performance Indicators
```python
# dr_metrics.py
class DisasterRecoveryMetrics:
    @staticmethod
    def calculate_metrics(incident):
        return {
            'detection_time': incident.detected_at - incident.occurred_at,
            'response_time': incident.first_response_at - incident.detected_at,
            'recovery_time': incident.resolved_at - incident.detected_at,
            'total_downtime': incident.resolved_at - incident.occurred_at,
            'data_loss': incident.data_loss_minutes,
            'affected_users': incident.affected_user_count,
            'met_rto': incident.recovery_time <= incident.rto,
            'met_rpo': incident.data_loss <= incident.rpo
        }
```

## Annual DR Review

### Review Checklist
- [ ] Update contact information
- [ ] Review and update procedures
- [ ] Test all backup systems
- [ ] Conduct full DR simulation
- [ ] Update technology stack changes
- [ ] Review vendor agreements
- [ ] Update compliance requirements
- [ ] Train new team members

### Improvement Plan
1. Identify gaps in current plan
2. Research new DR technologies
3. Update automation scripts
4. Enhance monitoring capabilities
5. Improve communication protocols

---

This disaster recovery plan should be reviewed quarterly and updated after any major infrastructure changes or incidents. All team members should be familiar with their roles and responsibilities during a disaster scenario.
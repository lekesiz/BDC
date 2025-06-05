"""
BDC Custom Metrics Exporter
Exposes application-specific metrics for Prometheus scraping
"""

import os
import time
import psutil
from datetime import datetime, timedelta
from flask import Flask, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import redis
import psycopg2
from sqlalchemy import create_engine, text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('bdc_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('bdc_request_duration_seconds', 'Request latency', ['endpoint'])
ACTIVE_USERS = Gauge('bdc_active_users', 'Number of active users')
TOTAL_USERS = Gauge('bdc_total_users', 'Total number of users')
TOTAL_BENEFICIARIES = Gauge('bdc_total_beneficiaries', 'Total number of beneficiaries')
TOTAL_PROGRAMS = Gauge('bdc_total_programs', 'Total number of programs')
TOTAL_EVALUATIONS = Gauge('bdc_total_evaluations', 'Total number of evaluations')
TOTAL_DOCUMENTS = Gauge('bdc_total_documents', 'Total number of documents')
ACTIVE_SESSIONS = Gauge('bdc_active_sessions', 'Number of active sessions')
CACHE_HIT_RATE = Gauge('bdc_cache_hit_rate', 'Cache hit rate percentage')
DATABASE_CONNECTIONS = Gauge('bdc_database_connections', 'Number of database connections')
BACKGROUND_TASKS = Gauge('bdc_background_tasks', 'Number of background tasks')
ERROR_RATE = Gauge('bdc_error_rate', 'Application error rate')
SYSTEM_HEALTH = Gauge('bdc_system_health', 'Overall system health score')

# Performance metrics
CPU_USAGE = Gauge('bdc_cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('bdc_memory_usage_percent', 'Memory usage percentage')
DISK_USAGE = Gauge('bdc_disk_usage_percent', 'Disk usage percentage')

class MetricsExporter:
    def __init__(self):
        self.db_engine = None
        self.redis_client = None
        self.app = Flask(__name__)
        self.setup_routes()
        self.setup_connections()

    def setup_connections(self):
        """Setup database and Redis connections"""
        try:
            # Database connection
            database_url = os.getenv('DATABASE_URL')
            if database_url:
                self.db_engine = create_engine(database_url)
                logger.info("Database connection established")
            
            # Redis connection
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            logger.info("Redis connection established")
            
        except Exception as e:
            logger.error(f"Error setting up connections: {str(e)}")

    def setup_routes(self):
        """Setup Flask routes"""
        @self.app.route('/metrics')
        def metrics():
            self.collect_metrics()
            return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

        @self.app.route('/health')
        def health():
            return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}

    def collect_metrics(self):
        """Collect all application metrics"""
        try:
            self.collect_database_metrics()
            self.collect_redis_metrics()
            self.collect_system_metrics()
            self.collect_application_metrics()
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")

    def collect_database_metrics(self):
        """Collect database-related metrics"""
        if not self.db_engine:
            return

        try:
            with self.db_engine.connect() as conn:
                # Count total users
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                TOTAL_USERS.set(result.scalar())

                # Count total beneficiaries
                result = conn.execute(text("SELECT COUNT(*) FROM beneficiaries"))
                TOTAL_BENEFICIARIES.set(result.scalar())

                # Count total programs
                result = conn.execute(text("SELECT COUNT(*) FROM programs"))
                TOTAL_PROGRAMS.set(result.scalar())

                # Count total evaluations
                result = conn.execute(text("SELECT COUNT(*) FROM evaluations"))
                TOTAL_EVALUATIONS.set(result.scalar())

                # Count total documents
                result = conn.execute(text("SELECT COUNT(*) FROM documents"))
                TOTAL_DOCUMENTS.set(result.scalar())

                # Count active users (logged in within last 24 hours)
                yesterday = datetime.now() - timedelta(days=1)
                result = conn.execute(text(
                    "SELECT COUNT(DISTINCT user_id) FROM user_activities WHERE created_at > :yesterday"
                ), yesterday=yesterday)
                ACTIVE_USERS.set(result.scalar())

                # Count database connections
                result = conn.execute(text("SELECT count(*) FROM pg_stat_activity"))
                DATABASE_CONNECTIONS.set(result.scalar())

        except Exception as e:
            logger.error(f"Error collecting database metrics: {str(e)}")

    def collect_redis_metrics(self):
        """Collect Redis-related metrics"""
        if not self.redis_client:
            return

        try:
            # Active sessions (assuming sessions are stored in Redis)
            session_keys = self.redis_client.keys('session:*')
            ACTIVE_SESSIONS.set(len(session_keys))

            # Cache statistics
            info = self.redis_client.info()
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0
            CACHE_HIT_RATE.set(hit_rate)

        except Exception as e:
            logger.error(f"Error collecting Redis metrics: {str(e)}")

    def collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            CPU_USAGE.set(cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            MEMORY_USAGE.set(memory.percent)

            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            DISK_USAGE.set(disk_percent)

        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")

    def collect_application_metrics(self):
        """Collect application-specific metrics"""
        try:
            # Background tasks (simulated - would need actual task queue integration)
            BACKGROUND_TASKS.set(0)  # Placeholder

            # Error rate (would need actual error tracking)
            ERROR_RATE.set(0.0)  # Placeholder

            # System health score (composite metric)
            health_score = self.calculate_health_score()
            SYSTEM_HEALTH.set(health_score)

        except Exception as e:
            logger.error(f"Error collecting application metrics: {str(e)}")

    def calculate_health_score(self):
        """Calculate overall system health score (0-100)"""
        try:
            score = 100
            
            # Database health
            if self.db_engine:
                try:
                    with self.db_engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                except:
                    score -= 30

            # Redis health
            if self.redis_client:
                try:
                    self.redis_client.ping()
                except:
                    score -= 20

            # System resources
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 80:
                score -= 15
            elif cpu_percent > 60:
                score -= 5

            if memory_percent > 85:
                score -= 15
            elif memory_percent > 70:
                score -= 5

            return max(0, score)

        except Exception as e:
            logger.error(f"Error calculating health score: {str(e)}")
            return 0

    def run(self):
        """Run the metrics exporter server"""
        port = int(os.getenv('METRICS_PORT', 8000))
        host = os.getenv('METRICS_HOST', '0.0.0.0')
        
        logger.info(f"Starting BDC Metrics Exporter on {host}:{port}")
        self.app.run(host=host, port=port, debug=False)

def main():
    """Main function to run the metrics exporter"""
    exporter = MetricsExporter()
    exporter.run()

if __name__ == '__main__':
    main()
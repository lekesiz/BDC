-- Initialize BDC Production Database
-- This script runs when the database is first created

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create application user (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'bdc_user') THEN
        CREATE USER bdc_user WITH ENCRYPTED PASSWORD 'placeholder_password';
    END IF;
END
$$;

-- Grant necessary permissions
GRANT CONNECT ON DATABASE bdc_production TO bdc_user;
GRANT USAGE ON SCHEMA public TO bdc_user;
GRANT CREATE ON SCHEMA public TO bdc_user;

-- Create read-only user for monitoring
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'bdc_monitor') THEN
        CREATE USER bdc_monitor WITH ENCRYPTED PASSWORD 'monitor_password';
    END IF;
END
$$;

-- Grant monitoring permissions
GRANT CONNECT ON DATABASE bdc_production TO bdc_monitor;
GRANT USAGE ON SCHEMA public TO bdc_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO bdc_monitor;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO bdc_monitor;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO bdc_monitor;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO bdc_monitor;

-- Create backup user
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'bdc_backup') THEN
        CREATE USER bdc_backup WITH ENCRYPTED PASSWORD 'backup_password';
    END IF;
END
$$;

-- Grant backup permissions
GRANT CONNECT ON DATABASE bdc_production TO bdc_backup;
GRANT USAGE ON SCHEMA public TO bdc_backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO bdc_backup;

-- Performance optimizations
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET pg_stat_statements.track = 'all';
ALTER SYSTEM SET log_statement = 'ddl';
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Reload configuration
SELECT pg_reload_conf();
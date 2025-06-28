-- Real Estate Platform Database Initialization
-- PostgreSQL 15+ required

-- Create additional schemas if needed
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS logs;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create indexes for performance
-- These will be created by Alembic migrations, but adding here for reference

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE realestate TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA logs TO postgres;

-- Log the initialization
INSERT INTO public.system_log (message) VALUES ('Database initialized successfully')
ON CONFLICT DO NOTHING;

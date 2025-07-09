-- Database initialization script for Wandr Backend API
-- This script is executed when the PostgreSQL container starts

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)
-- CREATE DATABASE IF NOT EXISTS wandr_db;

-- Enable PostGIS extension for geographic data support
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create additional extensions that might be useful
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For text search
CREATE EXTENSION IF NOT EXISTS btree_gin;  -- For indexing
CREATE EXTENSION IF NOT EXISTS btree_gist;  -- For indexing

-- Grant necessary permissions to the application user
-- (User is created automatically by POSTGRES_USER env var)
GRANT ALL PRIVILEGES ON DATABASE wandr_db TO wandr_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO wandr_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO wandr_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO wandr_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO wandr_user;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Note: Tables will be created by Alembic migrations
-- This script only sets up the database environment and extensions

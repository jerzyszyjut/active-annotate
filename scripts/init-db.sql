-- Initialize the database with any required setup
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)
-- Create any additional schemas, users, or extensions here if needed

-- Example: Create extensions
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- You can add any additional database initialization here

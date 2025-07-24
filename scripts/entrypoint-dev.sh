#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."

while ! pg_isready -h postgres -p 5432 -U postgres; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - ready for development"

# Don't run migrations automatically in development
# Developers can run them manually when needed

# Start the application
echo "Starting the development server..."
exec "$@"

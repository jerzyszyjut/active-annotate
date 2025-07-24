# Docker Development Guide

This guide explains how to use Docker for development and production deployment of the Active Annotate API.

## Prerequisites

- Docker
- Docker Compose
- Make (optional, for convenience commands)

## Quick Start

1. **Copy environment file:**

   ```bash
   cp .env.example .env
   ```

2. **Start development environment:**

   ```bash
   make up
   # or
   docker-compose -f docker-compose.dev.yml up -d
   ```

3. **Run database migrations:**

   ```bash
   make migrate
   # or
   docker-compose -f docker-compose.dev.yml exec api-dev alembic upgrade head
   ```

4. **Access the application:**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Interactive API Docs: http://localhost:8000/redoc

## Development Commands

### Using Make (Recommended)

```bash
# Start development environment
make up

# View logs
make logs

# Access API container shell
make shell

# Access database shell
make shell-db

# Run tests
make test

# Run migrations
make migrate

# Generate new migration
make migration MSG="Add new table"

# Stop environment
make down

# Clean up everything
make clean
```

### Using Docker Compose Directly

```bash
# Start services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Execute commands in containers
docker-compose -f docker-compose.dev.yml exec api-dev bash
docker-compose -f docker-compose.dev.yml exec postgres psql -U postgres -d active_annotate

# Stop services
docker-compose -f docker-compose.dev.yml down
```

## Available Services

### Development (docker-compose.dev.yml)

- **api-dev**: FastAPI application with hot reload
- **postgres**: PostgreSQL 15 database

### Production (docker-compose.prod.yml)

- **api**: FastAPI application (production build)
- **postgres**: PostgreSQL 15 database

## Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=active_annotate
POSTGRES_PORT=5432

# API
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## Database Management

### Running Migrations

```bash
# Upgrade to latest migration
make migrate

# Generate new migration
make migration MSG="Description of changes"

# Downgrade migration
docker-compose -f docker-compose.dev.yml exec api-dev alembic downgrade -1
```

### Database Access

```bash
# Access PostgreSQL shell
make shell-db

# Access with psql commands
docker-compose -f docker-compose.dev.yml exec postgres psql -U postgres -d active_annotate
```

### Reset Database

```bash
# Reset database (removes all data)
make reset-db
```

## Production Deployment

1. **Set production environment variables:**

   ```bash
   export POSTGRES_PASSWORD=your-secure-password
   export POSTGRES_USER=your-user
   ```

2. **Start production services:**

   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Run migrations:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
   ```

## Troubleshooting

### Common Issues

1. **Port conflicts:**

   - Change ports in docker-compose files if 5432 or 8000 are in use

2. **Database connection errors:**

   - Ensure PostgreSQL container is healthy: `docker-compose ps`
   - Check logs: `make logs-db`

3. **Permission errors:**
   - On Linux, you might need to adjust file permissions

### Useful Commands

```bash
# Check container status
docker-compose -f docker-compose.dev.yml ps

# View container resource usage
docker stats

# Remove unused Docker resources
docker system prune

# View Docker networks
docker network ls
```

## Development Workflow

1. Make code changes (files are mounted as volumes)
2. API automatically reloads (development mode)
3. Test changes using the API docs at http://localhost:8000/docs
4. Run tests: `make test`
5. Create migrations for model changes: `make migration MSG="description"`
6. Apply migrations: `make migrate`

## Additional Tools

### pgAdmin (Database GUI)

When using the full stack compose file:

- URL: http://localhost:5050
- Email: admin@example.com
- Password: admin

Add PostgreSQL server connection:

- Host: postgres
- Port: 5432
- Username: postgres
- Password: password
- Database: active_annotate

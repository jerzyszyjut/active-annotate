# Makefile for Active Annotate API

.PHONY: help build up down logs shell test clean migrate pgadmin

# Default target
help:
	@echo "Available commands:"
	@echo "  build      - Build Docker images"
	@echo "  up         - Start development environment"
	@echo "  up-prod    - Start production environment"
	@echo "  down       - Stop and remove containers"
	@echo "  logs       - Show logs from all services"
	@echo "  logs-api   - Show logs from API service"
	@echo "  logs-db    - Show logs from database service"
	@echo "  shell      - Open shell in API container"
	@echo "  shell-db   - Open shell in database container"
	@echo "  test       - Run tests in container"
	@echo "  test-cov   - Run tests with coverage report"
	@echo "  migrate    - Run database migrations"
	@echo "  migration  - Create migrations with given message"
	@echo "  clean      - Remove all containers, volumes and images"
	@echo "  reset-db   - Reset database (remove volume and restart)"
	@echo "  pgadmin    - Open pgAdmin in browser"

# Build Docker images
build:
	docker compose -f docker-compose.dev.yml build

# Start development environment
up:
	docker compose -f docker-compose.dev.yml up -d
	@echo "Development environment started!"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "pgAdmin: http://localhost:5050 (admin@example.com / admin)"

# Start production environment
up-prod:
	docker compose -f docker-compose.prod.yml up -d
	@echo "Production environment started!"
	@echo "API: http://localhost:8000"

# Stop containers
down:
	docker compose -f docker-compose.dev.yml down
	docker compose -f docker-compose.prod.yml down

# Show logs
logs:
	docker compose -f docker-compose.dev.yml logs -f

logs-api:
	docker compose -f docker-compose.dev.yml logs -f api-dev

logs-db:
	docker compose -f docker-compose.dev.yml logs -f postgres

# Open shell in API container
shell:
	docker compose -f docker-compose.dev.yml exec api-dev /bin/bash

# Open shell in database container
shell-db:
	docker compose -f docker-compose.dev.yml exec postgres psql -U postgres -d active_annotate

# Run tests
test:
	docker compose -f docker-compose.dev.yml exec api-dev pytest

# Run tests with coverage
test-cov:
	docker compose -f docker-compose.dev.yml exec api-dev pytest --cov=app --cov-report=xml --cov-report=term-missing --cov-report=html

# Run database migrations
migrate:
	docker compose -f docker-compose.dev.yml exec api-dev alembic upgrade head

# Generate new migration
migration:
	docker compose -f docker-compose.dev.yml exec api-dev alembic revision --autogenerate -m "$(MSG)"

# Clean up everything
clean:
	docker compose -f docker-compose.dev.yml down -v --rmi all
	docker compose -f docker-compose.prod.yml down -v --rmi all
	docker system prune -f

# Reset database
reset-db:
	docker compose -f docker-compose.dev.yml down
	docker volume rm active-annotate_postgres_dev_data || true
	docker compose -f docker-compose.dev.yml up -d postgres
	@echo "Database reset complete!"

# Install dependencies (for local development)
install:
	pipenv install --dev

# Format code
format:
	docker compose -f docker-compose.dev.yml exec api-dev ruff format .

# Lint code
lint:
	docker compose -f docker-compose.dev.yml exec api-dev ruff check .

# Check types
typecheck:
	docker compose -f docker-compose.dev.yml exec api-dev pyright

# Open pgAdmin in browser
pgadmin:
	@echo "Opening pgAdmin at http://localhost:5050"
	@echo "Login credentials:"
	@echo "  Email: admin@example.com"
	@echo "  Password: admin"
	@echo ""
	@echo "To connect to PostgreSQL in pgAdmin:"
	@echo "  Host: postgres"
	@echo "  Port: 5432"
	@echo "  Username: postgres"
	@echo "  Password: password"
	@echo "  Database: active_annotate"
	@which xdg-open > /dev/null 2>&1 && xdg-open http://localhost:5050 || \
	which open > /dev/null 2>&1 && open http://localhost:5050 || \
	echo "Please open http://localhost:5050 in your browser"

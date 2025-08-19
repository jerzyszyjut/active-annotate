# Multi-stage Dockerfile for Active Annotate API

# Base stage with Python and common dependencies
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install pipenv
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Development stage
FROM base AS development

# Install dependencies including dev dependencies
RUN pipenv install --dev --system --deploy

# Copy application code
COPY . .

# Copy and set permissions for entrypoint scripts
COPY scripts/entrypoint-dev.sh /entrypoint-dev.sh
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint-dev.sh /entrypoint.sh

# Expose port
EXPOSE 8000

# Set development entrypoint
ENTRYPOINT ["/entrypoint-dev.sh"]

# Command for development (with hot reload and multiple workers)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Production stage
FROM base AS production

# Install only production dependencies
RUN pipenv install --system --deploy

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Copy application code
COPY --chown=app:app . .

# Copy and set permissions for entrypoint script
COPY --chown=app:app scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Set production entrypoint (runs migrations)
ENTRYPOINT ["/entrypoint.sh"]

# Command for production (with multiple workers)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

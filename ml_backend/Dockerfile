FROM python:3.12-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=${PORT:-8000} \
    PIP_CACHE_DIR=/.cache

# Install system dependencies
RUN --mount=type=cache,target="/var/cache/apt",sharing=locked \
    --mount=type=cache,target="/var/lib/apt/lists",sharing=locked \
    set -eux; \
    apt-get update; \
    apt-get upgrade -y; \
    apt install --no-install-recommends -y  \
        wget \
        curl \
        git; \
    apt-get autoremove -y

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=${PIP_CACHE_DIR},sharing=locked \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create model weights directory with proper permissions
RUN mkdir -p /app/model_weights && chmod 777 /app/model_weights

# Expose port
EXPOSE $PORT

# Set Python path
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Run the FastAPI application with uvicorn and multiple workers
CMD uvicorn app:app --host 0.0.0.0 --port $PORT --workers 4

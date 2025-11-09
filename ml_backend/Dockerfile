FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip \
    zip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml .

RUN uv sync

RUN uv pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN uv pip install --no-cache-dir lightning torchmetrics

COPY . .

EXPOSE 9090

CMD ["uv", "run", "gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:9090"]

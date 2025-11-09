# Active Annotate

[![CI](https://github.com/jerzyszyjut/active-annotate/workflows/CI/badge.svg)](https://github.com/jerzyszyjut/active-annotate/actions)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-A30000?style=flat&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)](https://redis.io/)
[![MinIO](https://img.shields.io/badge/MinIO-C72C48?style=flat&logo=minio&logoColor=white)](https://min.io/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)
[![Documentation](https://img.shields.io/badge/docs-github--pages-blue)](https://jerzyszyjut.github.io/active-annotate/)

A comprehensive backend API for managing active learning annotation projects, built with Django REST Framework, PostgreSQL, and modern Python development practices.

## 📖 Documentation

The complete documentation for this project is available at:

**[https://jerzyszyjut.github.io/active-annotate/](https://jerzyszyjut.github.io/active-annotate/)**

The documentation includes:

- API reference and endpoints
- Installation instructions
- Development setup guide
- Testing procedures
- Project architecture overview

## 🎯 Features

- **Active Learning**: Intelligent data point selection using entropy-based uncertainty sampling
- **Model Management**: Integration with ML backends for model training and inference
- **Label Studio Integration**: Seamless integration with Label Studio for annotation tasks
- **Webhook Support**: Real-time annotation updates via webhooks
- **S3-Compatible Storage**: MinIO integration for media file storage
- **Async Task Management**: Celery for background tasks and periodic scheduling
- **Docker Support**: Full Docker Compose setup for local development and deployment
- **REST API**: Well-documented RESTful API with DRF

## 🚀 Quick Start

### Docker (Recommended)

1. Clone the repository:

```bash
git clone https://github.com/jerzyszyjut/active-annotate.git
cd active-annotate
```

2. Set up environment variables:

```bash
cp .envs/.local/.django.example .envs/.local/.django
cp .envs/.local/.postgres.example .envs/.local/.postgres
```

3. Start the development environment:

```bash
just up
```

4. Run database migrations:

```bash
just manage migrate
```

5. Create a superuser:

```bash
just manage createsuperuser
```

The services will be available at:

- **API**: `http://localhost:8000`
- **API Docs (Swagger)**: `http://localhost:8000/api/schema/swagger/`
- **API Docs (ReDoc)**: `http://localhost:8000/api/schema/redoc/`
- **Admin Panel**: `http://localhost:8000/admin`
- **MinIO Console**: `http://localhost:9001` (minioadmin / minioadmin)
- **Label Studio**: `http://localhost:8080`
- **Flower (Celery)**: `http://localhost:5555`

### Local Development (Alternative)

If you prefer local development without Docker:

#### Prerequisites

- Python 3.13+
- PostgreSQL 15+
- Redis 7+
- `uv` (for dependency management)

#### Installation

1. Clone the repository:

```bash
git clone https://github.com/jerzyszyjut/active-annotate.git
cd active-annotate
```

2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
uv sync
```

4. Set up environment variables:

```bash
cp .envs/.local/.django.example .envs/.local/.django
cp .envs/.local/.postgres.example .envs/.local/.postgres
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Create a superuser:

```bash
python manage.py createsuperuser
```

7. Start the development server:

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## 📝 Project Structure

```
active-annotate/
├── active_annotate/
│   ├── config/           # Django configuration
│   ├── datasets/         # Dataset management app
│   ├── integrations/     # External service integrations (Label Studio, ML Backend)
│   ├── users/            # User management app
│   └── manage.py
├── ml_backend/           # ML backend service (separate microservice)
├── compose/              # Docker compose configurations
├── docs/                 # Sphinx documentation
├── tests/                # Test suite
└── docker-compose.local.yml
```

## 🔧 Key Technologies

- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL 15+
- **Cache/Message Queue**: Redis 7+
- **Task Queue**: Celery with Celery Beat
- **File Storage**: MinIO (S3-compatible)
- **Annotation Tool**: Label Studio
- **Package Manager**: `uv`
- **Code Quality**: Ruff, mypy, djLint
- **Testing**: pytest with pytest-django
- **Documentation**: Sphinx with ReadTheDocs

## 💻 Available Commands

### Using `just` (recommended)

```bash
just --list          # List all available commands
just build          # Build Docker images
just up             # Start containers
just down           # Stop containers
just prune          # Remove containers and volumes
just logs [service] # View container logs
just manage [cmd]   # Run Django management commands
```

### Using `uv` directly

```bash
uv run python manage.py [command]  # Run management commands
uv run pytest                      # Run tests
uv run coverage run -m pytest      # Run tests with coverage
```

## 👤 User Management

### Creating Users

- To create a **normal user account**, go to the Sign Up endpoint and fill out the form. Once submitted, you'll receive an email verification link.

- To create a **superuser account**, use:

```bash
just manage createsuperuser
# or for local development
uv run python manage.py createsuperuser
```

For convenience during development, you can keep your normal user logged in on one browser tab and your superuser logged in on another tab to see how the site behaves for different user types.

## 🧪 Testing

### Docker (Recommended)

Run all tests:

```bash
just manage test
```

### Local Development

```bash
# Run all tests
uv run pytest

# Run tests with coverage report
uv run coverage run -m pytest
uv run coverage html
uv run open htmlcov/index.html

# Run specific test file
uv run pytest tests/test_specific.py

# Run with verbose output
uv run pytest -v
```

## 📊 Code Quality

### Type Checking

Running type checks with mypy:

```bash
uv run mypy active_annotate
```

### Code Formatting and Linting

The project uses Ruff for linting and code style. Configuration is in `pyproject.toml`.

```bash
# Check code style
uv run ruff check active_annotate

# Format code
uv run ruff format active_annotate
```

### Django Template Linting

```bash
uv run djlint --check active_annotate/templates/
uv run djlint --reformat active_annotate/templates/
```

## 🔄 Celery

This app comes with Celery for background task management and scheduled jobs.

### Running Celery Worker

```bash
uv run celery -A config.celery_app worker -l info
```

### Running Celery Beat (Periodic Tasks)

```bash
uv run celery -A config.celery_app beat
```

### Using Beat with Worker (Development Only)

```bash
uv run celery -A config.celery_app worker -B -l info
```

### Monitoring with Flower

```bash
uv run celery -A config.celery_app flower
```

Access Flower at `http://localhost:5555`

## 📚 Documentation Development

To build the documentation locally:

```bash
cd docs
uv run make html
```

The built documentation will be available in `docs/_build/html/index.html`

## 🔗 API Integration Examples

### Label Studio Webhook Integration

The system receives webhook events from Label Studio when annotations are created or updated. Webhooks are automatically configured when creating an active learning project.

**Webhook Event Types:**
- `ANNOTATION_CREATED` - New annotation added
- `ANNOTATION_UPDATED` - Annotation modified

### ML Backend Integration

The system can integrate with ML backends for:
- **Model Status Checks**: Monitor model training and inference readiness
- **Predictions**: Generate predictions for unlabeled data points
- **Model Training**: Train models on labeled data

### Active Learning Strategy

The system implements entropy-based uncertainty sampling to select the most informative data points for annotation:

```python
# Uncertainty is calculated based on prediction entropy
# Higher entropy = more uncertain = higher priority for annotation
uncertainty = -sum(p * log(p) for p in normalized_confidences)
```

## 🌍 Environment Variables

### Django Configuration

```env
# Core
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=active_annotate
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Redis
REDIS_URL=redis://redis:6379

# AWS/MinIO
AWS_STORAGE_BUCKET_NAME=media
AWS_S3_ACCESS_KEY_ID=minioadmin
AWS_S3_SECRET_ACCESS_KEY=minioadmin
AWS_S3_ENDPOINT_URL=http://minio:9000
AWS_S3_FRONTEND_URL=http://localhost:9000

# Label Studio
LABEL_STUDIO_URL=http://label_studio:8080
LABEL_STUDIO_API_KEY=your-label-studio-api-key

# Email (for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🤝 Contributing

Please refer to our [development documentation](https://jerzyszyjut.github.io/active-annotate/development.html) for detailed contribution guidelines.

We welcome contributions! Please feel free to submit issues and pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Jerzy Szyjut** - Initial development and architecture
- **Hubert Malinowski** - Contributions and development

## 🙏 Acknowledgments

Built with:
- [Cookiecutter Django](https://github.com/cookiecutter/cookiecutter-django/) - Project template
- [Django REST Framework](https://www.django-rest-framework.org/) - API framework
- [Label Studio](https://labelstud.io/) - Annotation tool
- [MinIO](https://min.io/) - S3-compatible object storage
- [Celery](https://docs.celeryq.dev/) - Distributed task queue
- The amazing Python and Django communities

## 📞 Support

For issues, questions, or suggestions, please open an issue on [GitHub](https://github.com/jerzyszyjut/active-annotate/issues).

---

**Last Updated**: November 2024

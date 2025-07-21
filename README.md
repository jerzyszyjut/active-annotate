# Active Annotate API

A FastAPI-based backend application for managing active learning annotation projects. This system provides a robust API for handling projects, datapoints, annotations, machine learning models, and active learning methods.

## Features

- **Project Management**: Create and manage annotation projects
- **Data Management**: Handle datapoints and their annotations
- **Active Learning**: Implement and manage active learning methods
- **Model Integration**: Support for ML model training and inference
- **Annotation Services**: External annotation service integration
- **Async Support**: Built on FastAPI with async/await support
- **Type Safety**: Full type checking with Pyright
- **Database**: PostgreSQL with SQLModel/SQLAlchemy
- **Docker**: Containerized deployment
- **CI/CD**: GitHub Actions workflow
- **Testing**: Comprehensive test suite with pytest

## Technology Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with asyncpg driver
- **ORM**: SQLModel (built on SQLAlchemy 2.0)
- **Migration**: Alembic
- **Type Checking**: Pyright
- **Linting**: Ruff
- **Formatting**: Black, isort
- **Testing**: pytest, pytest-asyncio
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

## Project Structure

```
active-annotate/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── projects.py
│   │   │   ├── datapoints.py
│   │   │   ├── annotations.py
│   │   │   ├── models.py
│   │   │   ├── al_methods.py
│   │   │   └── annotation_services.py
│   │   └── routes.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   └── __init__.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   └── test_projects.py
├── alembic/
│   └── versions/
├── docker-compose.yml
├── Dockerfile
├── Pipfile
├── Pipfile.lock
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Domain Model

The application is built around these core entities:

- **Project**: Container for annotation tasks with active learning configuration
- **Datapoint**: Individual data items to be annotated
- **Annotation**: Human or machine annotations for datapoints
- **Model**: ML models for inference and training
- **ALMethod**: Active learning methods for selecting datapoints
- **AnnotationService**: External services for annotation tasks

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jerzyszyjut/active-annotate.git
   cd active-annotate
   ```

2. **Install dependencies**:
   ```bash
   # Install pipenv if you haven't already
   pip install pipenv
   
   # Install project dependencies
   pipenv install --dev
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up database**:
   ```bash
   # Start PostgreSQL (using Docker)
   docker run -d --name postgres-dev \
     -e POSTGRES_DB=active_annotate \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=password \
     -p 5432:5432 \
     postgres:16-alpine
   
   # Run migrations
   pipenv run alembic upgrade head
   ```

5. **Run the application**:
   ```bash
   pipenv run uvicorn app.main:app --reload
   ```

6. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc
   - Health check: http://localhost:8000/health

### Using Docker Compose

For a complete development environment with database:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## API Endpoints

### Projects
- `POST /api/v1/projects/` - Create a new project
- `GET /api/v1/projects/` - List all projects
- `GET /api/v1/projects/{id}` - Get project by ID
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Datapoints
- `POST /api/v1/datapoints/` - Create a new datapoint
- `GET /api/v1/datapoints/` - List datapoints (filterable by project)
- `GET /api/v1/datapoints/{id}` - Get datapoint by ID
- `PUT /api/v1/datapoints/{id}` - Update datapoint
- `DELETE /api/v1/datapoints/{id}` - Delete datapoint

### Annotations
- `POST /api/v1/annotations/` - Create a new annotation
- `GET /api/v1/annotations/` - List annotations (filterable by datapoint)
- `GET /api/v1/annotations/{id}` - Get annotation by ID
- `PUT /api/v1/annotations/{id}` - Update annotation
- `DELETE /api/v1/annotations/{id}` - Delete annotation

### Models
- `POST /api/v1/models/` - Create a new model
- `GET /api/v1/models/` - List models (filterable by project)
- `GET /api/v1/models/{id}` - Get model by ID
- `PUT /api/v1/models/{id}` - Update model
- `DELETE /api/v1/models/{id}` - Delete model
- `POST /api/v1/models/{id}/train` - Train model

### AL Methods
- `POST /api/v1/al-methods/` - Create a new AL method
- `GET /api/v1/al-methods/` - List AL methods (filterable by project)
- `GET /api/v1/al-methods/{id}` - Get AL method by ID
- `PUT /api/v1/al-methods/{id}` - Update AL method
- `DELETE /api/v1/al-methods/{id}` - Delete AL method
- `POST /api/v1/al-methods/{id}/calculate-score` - Calculate annotation score

### Annotation Services
- `POST /api/v1/annotation-services/` - Create a new service
- `GET /api/v1/annotation-services/` - List services
- `GET /api/v1/annotation-services/{id}` - Get service by ID
- `PUT /api/v1/annotation-services/{id}` - Update service
- `DELETE /api/v1/annotation-services/{id}` - Delete service
- `POST /api/v1/annotation-services/{id}/add-annotation` - Add annotation via service
- `POST /api/v1/annotation-services/{id}/get-preannotation` - Get preannotation

## Development

### Code Quality

The project uses several tools to maintain code quality:

```bash
# Type checking
pipenv run pyright

# Linting
pipenv run ruff check .

# Formatting
pipenv run black .
pipenv run isort .

# Run all checks
pipenv run ruff check . && pipenv run black --check . && pipenv run pyright && pipenv run isort --check-only .
```

### Testing

```bash
# Run all tests
pipenv run pytest

# Run with coverage
pipenv run pytest --cov=app --cov-report=html

# Run specific test file
pipenv run pytest tests/test_projects.py

# Run with verbose output
pipenv run pytest -v
```

### Database Migrations

```bash
# Create a new migration
pipenv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
pipenv run alembic upgrade head

# Rollback migration
pipenv run alembic downgrade -1
```

### Adding New Features

1. Update models in `app/models/__init__.py`
2. Create database migration with Alembic
3. Add API endpoints in `app/api/endpoints/`
4. Update router in `app/api/routes.py`
5. Write tests in `tests/`
6. Update documentation

## Configuration

Environment variables (see `.env.example`):

- `POSTGRES_SERVER`: Database host
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name
- `POSTGRES_PORT`: Database port
- `SECRET_KEY`: Secret key for security
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins

## Deployment

### Production with Docker

1. Build the Docker image:
   ```bash
   docker build -t active-annotate .
   ```

2. Run with production database:
   ```bash
   docker run -d \
     --name active-annotate-prod \
     -p 8000:8000 \
     -e POSTGRES_SERVER=your-db-host \
     -e POSTGRES_USER=your-db-user \
     -e POSTGRES_PASSWORD=your-db-password \
     -e SECRET_KEY=your-secret-key \
     active-annotate
   ```

### CI/CD

The project includes GitHub Actions workflow for:
- Code quality checks (linting, formatting, type checking)
- Running tests with PostgreSQL
- Building and pushing Docker images

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests and quality checks
5. Commit your changes: `git commit -am 'Add some feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues, please create an issue on GitHub.

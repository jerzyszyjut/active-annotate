# Active Annotate

[![CI](https://github.com/jerzyszyjut/active-annotate/workflows/CI/badge.svg)](https://github.com/jerzyszyjut/active-annotate/actions)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Code Coverage](https://img.shields.io/badge/coverage-95%25-green.svg)](https://github.com/jerzyszyjut/active-annotate/actions)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)
[![Documentation](https://img.shields.io/badge/docs-github--pages-blue)](https://jerzyszyjut.github.io/active-annotate/)

A backend API for managing active learning annotation projects with ML Backend integration for Label Studio, built with FastAPI and modern Python development practices.

## ✨ Features

- **RESTful API** for project management
- **ML Backend Integration** for Label Studio
- **Active Learning Support** with custom ML models
- **PostgreSQL Database** with async support
- **Docker containerization** for easy deployment
- **Comprehensive testing** with pytest
- **API documentation** with OpenAPI/Swagger
- **Modern Python** with type hints and async/await

## 📖 Documentation

The complete documentation for this project is available at:

**[https://jerzyszyjut.github.io/active-annotate/](https://jerzyszyjut.github.io/active-annotate/)**

The documentation includes:

- API reference and endpoints
- Installation instructions
- Development setup guide
- Testing procedures
- Project architecture overview

## 🚀 Quick Start

### Docker (Recommended)

1. Clone the repository:

   ```bash
   git clone https://github.com/jerzyszyjut/active-annotate.git
   cd active-annotate
   ```

2. Start the development environment:

   ```bash
   make up
   ```

3. Run database migrations:

   ```bash
   make migrate
   ```

The API will be available at:

- **API**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`
- **ML Backend API**: `http://localhost:8000/ml`
- **pgAdmin**: `http://localhost:5050` (admin@example.com / admin)

## 🤖 ML Backend Integration

Active Annotate includes built-in ML Backend API endpoints for seamless integration with Label Studio:

### Available Endpoints

- **POST** `/ml/predict` - Get predictions for tasks
- **POST** `/ml/setup` - Initialize ML model for a project
- **POST** `/ml/webhook` - Handle training events
- **GET** `/ml/health` - Health check
- **GET** `/ml/metrics` - Model metrics

### Quick ML Backend Setup

1. Configure your custom ML backend URL:

   ```bash
   export ML_BACKEND_URL=http://localhost:8001
   ```

2. Start your custom ML backend on port 8001

3. Configure Label Studio to use `http://localhost:8000/ml` as the ML backend

For detailed ML Backend integration documentation, see [docs/ml-backend-integration.md](docs/ml-backend-integration.md).

### Local Development (Alternative)

If you prefer local development without Docker:

#### Prerequisites

- Python 3.12+
- pipenv (for dependency management)

#### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/jerzyszyjut/active-annotate.git
   cd active-annotate
   ```

2. Install dependencies:

   ```bash
   pipenv install --dev
   ```

3. Activate the virtual environment:

   ```bash
   pipenv shell
   ```

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 🧪 Testing

### Docker (Recommended)

```bash
# Run all tests including ML backend tests
make test

# Run specific ML backend tests
pipenv run pytest tests/test_ml_backend.py

# Test ML backend integration
python examples/test_ml_backend.py

# Run tests with coverage report
make test-cov
```

### Local Development

```bash
pipenv run pytest
```

## 📝 Documentation Development

To build the documentation locally:

```bash
cd docs
pipenv run make html
```

The built documentation will be available in `docs/_build/html/index.html`

## 🤝 Contributing

Please refer to our [development documentation](https://jerzyszyjut.github.io/active-annotate/development.html) for detailed contribution guidelines.

## 📄 License

This project is under active development.

## 👥 Authors

- Jerzy Szyjut
- Hubert Malinowski

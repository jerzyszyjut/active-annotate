# Active Annotate

[![CI](https://github.com/jerzyszyjut/active-annotate/workflows/CI/badge.svg)](https://github.com/jerzyszyjut/active-annotate/actions)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Code Coverage](https://img.shields.io/badge/coverage-77%25-yellow.svg)](https://github.com/jerzyszyjut/active-annotate/actions)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)
[![Documentation](https://img.shields.io/badge/docs-github--pages-blue)](https://jerzyszyjut.github.io/active-annotate/)

A backend API for managing active learning annotation projects, built with FastAPI and modern Python development practices.

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
- **pgAdmin**: `http://localhost:5050` (admin@example.com / admin)

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
# Run all tests
make test

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

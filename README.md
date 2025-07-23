# Active Annotate

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

### Prerequisites

- Python 3.12+
- pipenv (for dependency management)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/jerzyszyjut/active-annotate.git
   cd active-annotate
   ```

2. Install dependencies:

   ```bash
   pipenv install
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

Run the test suite:

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

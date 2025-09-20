# Contributing to Django Dart Sass

Thank you for your interest in contributing to Django Dart Sass! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for dependency management
- Git

### Getting Started

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/django-dart-sass.git
   cd django-dart-sass
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Install pre-commit hooks** (optional but recommended)
   ```bash
   uv run pre-commit install
   ```

4. **Run tests to ensure everything works**
   ```bash
   uv run pytest
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=django_dart_sass

# Run specific test file
uv run pytest tests/test_functions.py

# Run specific test
uv run pytest tests/test_functions.py::TestDjangoFunctions::test_static_function
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code
uv run black .
uv run isort .

# Check formatting
uv run black --check .
uv run isort --check-only .

# Lint code
uv run ruff check .

# Type checking
uv run mypy src/django_dart_sass
```

### Testing Django Compressor Integration

To test django-compressor integration:

```bash
# Install dev dependencies (includes django-compressor)
uv sync

# Run compressor tests
uv run pytest tests/test_compressor.py
```

## Project Structure

```
django-dart-sass/
├── src/
│   └── django_dart_sass/
│       ├── __init__.py          # Main API exports
│       ├── apps.py              # Django app configuration
│       ├── compressor.py        # django-compressor integration
│       ├── decorators.py        # Function/importer decorators
│       ├── functions.py         # Built-in Django functions
│       ├── importers.py         # Django importer system
│       └── registry.py          # Two-tier registry system
├── tests/
│   ├── conftest.py              # Test configuration
│   ├── settings.py              # Django test settings
│   ├── test_compressor.py       # Compressor integration tests
│   ├── test_functions.py        # Function system tests
│   ├── test_importers.py        # Importer system tests
│   ├── test_integration.py      # End-to-end integration tests
│   └── test_performance.py      # Performance tests
├── pyproject.toml               # Project configuration
└── README.md                    # Project documentation
```

## Architecture Overview

### Two-Tier System

The package implements a two-tier architecture for both functions and importers:

1. **Global Tier**: Functions/importers registered via decorators (`@sass_function`, `@sass_importer`)
   - Permanent across all compilations
   - Registered when modules are imported
   - Ideal for Django-specific functions

2. **Contextual Tier**: Functions/importers passed to specific compile calls
   - Scoped to individual compilations
   - Higher priority than global tier
   - Ideal for one-off customizations

### Key Components

- **Registry System** (`registry.py`): Merges global and contextual functions/importers
- **Decorator System** (`decorators.py`): Manages global function/importer registration
- **Django Functions** (`functions.py`): Built-in Django-specific Sass functions
- **Django Importer** (`importers.py`): Handles app-specific imports and Django static files
- **Compressor Integration** (`compressor.py`): django-compressor filter implementation

## Contributing Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep line length to 88 characters (Black default)

### Testing

- Write tests for all new functionality
- Maintain 100% test coverage for core functionality
- Use descriptive test names that explain what is being tested
- Group related tests in classes
- Use Django's `TestCase` for tests that need Django functionality

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all public APIs
- Include code examples in docstrings
- Update CHANGELOG.md for all changes

### Commit Messages

Use clear, descriptive commit messages:

```
Add support for custom theme color functions

- Implement theme-color() Sass function
- Add SASS_THEME_COLORS setting support
- Include comprehensive tests for color handling
- Update documentation with usage examples
```

## Types of Contributions

### Bug Reports

When reporting bugs, please include:

- Python version
- Django version
- django-dart-sass version
- Minimal code example that reproduces the issue
- Full error traceback
- Expected vs actual behavior

### Feature Requests

For new features, please:

- Describe the use case and motivation
- Provide examples of how the feature would be used
- Consider backward compatibility
- Discuss implementation approach if you have ideas

### Code Contributions

1. **Create an issue** first to discuss the change
2. **Fork the repository** and create a feature branch
3. **Implement the change** with tests and documentation
4. **Ensure all tests pass** and code quality checks pass
5. **Submit a pull request** with a clear description

### Documentation Improvements

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add more examples
- Improve API documentation
- Add tutorials or guides

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with new version
3. Create a git tag: `git tag v1.0.0`
4. Push tag: `git push origin v1.0.0`
5. Build and publish to PyPI: `uv build && uv publish`

## Getting Help

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and general discussion
- **Email**: Contact maintainers directly for security issues

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

## License

By contributing to Django Dart Sass, you agree that your contributions will be licensed under the MIT License.

# Contributing to doc23

Thank you for your interest in contributing to doc23! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct.

## How to Contribute

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`make test` and `make lint`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/alexvargashn/doc23.git
cd doc23
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

## Testing

We use pytest for testing. To run tests:

```bash
make test
```

Or directly:
```bash
pytest tests/
```

## Code Style

We use the following tools for code quality:

- black for code formatting
- flake8 for linting
- mypy for type checking

Run all checks:
```bash
make lint
```

## Documentation

- Update README.md for user-facing changes
- Update CHANGELOG.md for all changes
- Add docstrings to new functions/classes
- Update ADVANCED_USAGE_doc23.md for advanced features

## Pull Request Process

1. Ensure your code passes all tests and linting checks
2. Update documentation as needed
3. Update CHANGELOG.md
4. Provide a clear description of your changes
5. Reference any related issues

## Questions?

Feel free to open an issue if you have any questions about contributing! 
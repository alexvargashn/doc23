# 🤝 Contributing to doc23

First of all, thank you for your interest in contributing to **doc23**! 🚀  
This document provides guidelines for contributing to ensure a consistent, high-quality, and welcoming collaboration.

---

## 📑 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Code Style](#code-style)
- [Documentation](#documentation)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Contact](#contact)

---

## 🧭 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct.  
(Coming soon in `CODE_OF_CONDUCT.md`.)

---

## 🛠 How to Contribute

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Make your changes.
4. Run tests and linting:
   ```bash
   make test
   make lint
   ```
5. Commit your changes:
   ```bash
   git commit -m 'feat: add amazing feature'
   ```
6. Push to your branch:
   ```bash
   git push origin feature/amazing-feature
   ```
7. Open a Pull Request to the `main` branch.

---

## 🖥️ Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/alexvargashn/doc23.git
   cd doc23
   ```

2. Create and activate a virtual environment:
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

---

## 🧪 Testing

We use **pytest** for testing.

To run all tests:
```bash
make test
```
Or manually:
```bash
pytest tests/
```

Please ensure that all tests pass before submitting a pull request.

---

## 🧹 Code Style

We maintain code quality using:
- **black** for code formatting
- **flake8** for linting
- **mypy** for type checking

Run all checks:
```bash
make lint
```

**Additional Guidelines:**
- Follow **PEP 8** style conventions.
- Use **type hints** wherever possible.
- Comments and docstrings must be written in **English**.
- Keep functions **small and single-responsibility**.

---

## 📚 Documentation

When contributing:
- Update `README.md` if you introduce new features or changes visible to users.
- Add entries to `CHANGELOG.md` for all significant changes.
- Update or add docstrings to new or modified classes and functions.
- Update `ADVANCED_USAGE_doc23.md` if you touch advanced functionality.

---

## 📝 Commit Messages

Use clear, conventional commit messages.  
Recommended prefixes:
- `feat:` for new features
- `fix:` for bug fixes
- `chore:` for maintenance tasks
- `docs:` for documentation updates
- `test:` for adding or fixing tests
- `refactor:` for code structure changes (no behavior change)

**Examples:**
```bash
git commit -m "feat: add support for Markdown documents"
git commit -m "fix: handle OCR parsing edge cases"
```

If a commit closes an issue, reference it:
```bash
git commit -m "fix: correct parsing error in docx files (#42)"
```

---

## 📦 Pull Request Process

1. Ensure all tests and linting checks pass.
2. Update documentation if needed.
3. Update `CHANGELOG.md` with a brief description of your changes.
4. Open a Pull Request using the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE/pull_request_template.md).
5. Follow the checklist in the Pull Request to ensure completeness.
6. Provide a clear description of what was changed and why.
7. Reference related issues if applicable (e.g., `Closes #42`).

---

## 🐛 Reporting Bugs

If you find a bug, please open an [issue](https://github.com/alexvargashn/doc23/issues/new?assignees=&labels=bug&template=bug_report.md) and provide:
- A clear and concise title (e.g., `[BUG] Parsing fails with large PDFs`)
- Steps to reproduce the behavior
- Expected vs actual behavior
- Environment details (OS, Python version, doc23 version)

Use the **Bug Report Template** to ensure consistency.

---

## 📫 Contact

If you have questions, suggestions, or feedback, feel free to:
- Open an [Issue](https://github.com/alexvargashn/doc23/issues)
- Contact [Alex Vargas](https://github.com/alexvargashn) directly through GitHub

---

Thanks again for helping improve **doc23**! 🙌  
Together we are building a powerful tool for document parsing and legaltech innovation.

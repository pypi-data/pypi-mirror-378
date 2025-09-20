# Invisibles

[![PyPI version](https://badge.fury.io/py/invisibles.svg)](https://badge.fury.io/py/invisibles)
[![Python Support](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern Python library for transparent remote object proxying.
Invisibles provides a powerful and intuitive way to create transparent proxies that forward all operations to wrapped objects while remaining completely invisible in most contexts.

## Features

- **Transparent proxying**: The proxy forwards all attribute access, method calls, and operations to the wrapped object
- **Complete operation support**: Supports all Python dunder methods for seamless integration
- **Type preservation**: Maintains the apparent type and behavior of the wrapped object
- **Zero overhead**: Minimal performance impact with efficient forwarding
- **Modern Python**: Built for Python 3.12+ with full type hint support

## Installation

```bash
pip install invisibles
```

## Development

### Setting up for development

```bash
# Clone the repository
git clone https://github.com/yourusername/invisibles.git
cd invisibles

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

### Running tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=invisibles --cov-report=term-missing
```

### Code quality

```bash
# Format code
poetry run black src tests

# Sort imports
poetry run isort src tests

# Lint code
poetry run flake8 src tests

# Type checking
poetry run mypy src
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

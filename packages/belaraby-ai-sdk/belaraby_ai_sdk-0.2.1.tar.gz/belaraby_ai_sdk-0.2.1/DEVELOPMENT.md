# BelArabyAI SDK Development Guide

This guide covers development, testing, and publishing of the BelArabyAI SDK.

## 🛠️ Development Setup

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/belarabyai/belarabyai.git
   cd belarabyai/sdk
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

   Or with uv:
   ```bash
   uv sync --dev
   ```

### Development Environment

The SDK uses modern Python tooling:

- **Build System**: Hatchling (configured in `pyproject.toml`)
- **Code Formatting**: Black
- **Import Sorting**: isort
- **Linting**: Ruff
- **Type Checking**: mypy
- **Testing**: pytest with pytest-asyncio

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=ba --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run tests with verbose output
pytest -v
```

### Test Structure

- `tests/conftest.py` - Test configuration and fixtures
- `tests/test_*.py` - Individual test modules
- `tests/test_integration.py` - Integration tests

### Writing Tests

Follow these guidelines:

1. **Use fixtures** from `conftest.py` for common setup
2. **Mock external dependencies** (API calls, MCP servers)
3. **Test both success and error cases**
4. **Use descriptive test names**
5. **Group related tests in classes**

Example:
```python
class TestMyClass:
    """Test cases for MyClass."""
    
    @pytest.fixture
    def my_instance(self):
        """Create a test instance."""
        return MyClass()
    
    def test_success_case(self, my_instance):
        """Test successful operation."""
        result = my_instance.do_something()
        assert result == expected_value
    
    def test_error_case(self, my_instance):
        """Test error handling."""
        with pytest.raises(ValueError):
            my_instance.do_something_invalid()
```

## 🔧 Code Quality

### Formatting and Linting

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with Ruff
ruff check .

# Type check with mypy
mypy ba/
```

### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:

```bash
pip install pre-commit
pre-commit install
```

## 📦 Building and Publishing

### Building the Package

```bash
# Build the package
python scripts/build.py

# Or manually:
python -m build
```

This creates:
- `dist/belarabyai-*.whl` - Wheel distribution
- `dist/belarabyai-*.tar.gz` - Source distribution

### Testing the Package

```bash
# Install the built package locally
pip install dist/belarabyai-*.whl

# Test installation
python -c "import belarabyai; print(belarabyai.__version__)"
```

### Publishing to PyPI

#### TestPyPI (Recommended for testing)

```bash
# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ belarabyai
```

#### Production PyPI

```bash
# Upload to production PyPI
python scripts/publish.py

# Or manually:
python -m twine upload dist/*
```

### Version Management

Update the version in `pyproject.toml`:

```toml
[project]
version = "0.1.1"  # Update this
```

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## 📁 Project Structure

```
sdk/
├── ba/                    # Main package
│   ├── __init__.py
│   ├── ba.py             # Main SDK class
│   ├── models.py         # Data models
│   ├── agent.py          # Agent management
│   ├── thread.py         # Thread management
│   ├── tools.py          # Tool definitions
│   ├── utils.py          # Utilities
│   └── api/              # API clients
│       ├── agents.py
│       ├── threads.py
│       └── utils.py
├── tests/                # Test suite
├── examples/             # Usage examples
├── scripts/              # Build/publish scripts
├── pyproject.toml        # Package configuration
├── README.md            # User documentation
├── DEVELOPMENT.md        # This file
└── MANIFEST.in          # Package manifest
```

## 🔍 Debugging

### Common Issues

1. **Import errors**: Check that all dependencies are installed
2. **API errors**: Verify API key and network connectivity
3. **MCP errors**: Ensure fastmcp is installed and MCP server is running
4. **Test failures**: Check that mocks are properly configured

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run the test suite**: `pytest`
6. **Format your code**: `black . && isort .`
7. **Commit your changes**: `git commit -m 'Add amazing feature'`
8. **Push to the branch**: `git push origin feature/amazing-feature`
9. **Open a Pull Request**

### Code Review Checklist

- [ ] Tests pass
- [ ] Code is formatted and linted
- [ ] Documentation is updated
- [ ] Examples work correctly
- [ ] No breaking changes (or properly documented)

## 📚 Documentation

### User Documentation

- `README.md` - Main user guide
- `examples/` - Practical examples
- `examples/README.md` - Example documentation

### Developer Documentation

- `DEVELOPMENT.md` - This file
- `pyproject.toml` - Package configuration
- Docstrings in code

### API Documentation

Generate API documentation:

```bash
pip install sphinx sphinx-rtd-theme
sphinx-build -b html docs/ docs/_build/
```

## 🚀 Release Process

### Pre-release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Version is bumped
- [ ] CHANGELOG is updated
- [ ] Examples are tested

### Release Steps

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with new features/fixes
3. **Run tests**: `pytest`
4. **Build package**: `python scripts/build.py`
5. **Test package**: Install and test locally
6. **Publish**: `python scripts/publish.py`
7. **Create GitHub release** with changelog

## 🆘 Getting Help

- **Issues**: [GitHub Issues](https://github.com/belarabyai/belarabyai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/belarabyai/belarabyai/discussions)
- **Email**: mk@belaraby.com
- **Documentation**: [https://docs.belaraby.ai](https://docs.belaraby.ai)

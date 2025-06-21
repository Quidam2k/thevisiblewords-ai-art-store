# Python Dependencies

```txt
# Core dependencies
pyyaml>=6.0
watchdog>=3.0.0
pillow>=9.0.0
requests>=2.28.0
pydantic>=1.10.0

# Optional dependencies for enhanced functionality
nltk>=3.8
aiohttp>=3.8.0
aiofiles>=22.1.0

# Development dependencies (optional)
pytest>=7.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
```

## Dependency Explanations

### Core Dependencies

- **pyyaml**: YAML configuration file parsing and validation
- **watchdog**: Cross-platform file system event monitoring for detecting new images
- **pillow**: Image processing library for optimization and metadata extraction
- **requests**: HTTP client for Printify API interactions
- **pydantic**: Data validation and settings management using Python type annotations

### Optional Dependencies

- **nltk**: Natural Language Toolkit for advanced prompt processing and tag extraction
- **aiohttp**: Asynchronous HTTP client for concurrent API requests
- **aiofiles**: Asynchronous file operations for better performance

### Development Dependencies

- **pytest**: Testing framework for unit and integration tests
- **black**: Code formatter for consistent Python code style
- **flake8**: Linting tool for code quality checks
- **mypy**: Static type checker for Python

## Installation

Install core dependencies only:
```bash
pip install pyyaml watchdog pillow requests pydantic
```

Install all dependencies including optional ones:
```bash
pip install -r requirements.txt
```

Install development dependencies:
```bash
pip install -r requirements.txt
pip install pytest black flake8 mypy
```

## Version Notes

- **Python 3.8+** required
- **Pillow 9.0+** required for modern image format support
- **Pydantic 1.10+** required for enhanced validation features
- **Watchdog 3.0+** required for improved cross-platform compatibility
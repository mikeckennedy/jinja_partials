# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Setup
```bash
pip install -e .              # Install package in editable mode
pip install -r requirements-dev.txt  # Install development dependencies
```

### Testing
```bash
pytest                        # Run all tests
pytest tests/test_rendering.py # Run specific test file
pytest -k "test_render_empty"  # Run specific test by name
pytest -v                     # Verbose output with test names
```

### Linting and Formatting
```bash
ruff check                    # Run linter (E, F, I checks)
ruff format                   # Format code (uses single quotes, 120 line length)
```

### Building and Publishing
```bash
hatchling build               # Build distribution packages
# Publishing handled by project maintainer
```

## Architecture Overview

This is a single-module Python library that extends Jinja2 with partial template rendering capabilities. The core architecture consists of:

- **Core API**: `render_partial()` function that renders HTML fragments with data, returning either `Markup` or `str`
- **Registration Functions**: Framework-specific helpers (`register_extensions`, `register_starlette_extensions`, `register_environment`) that inject `render_partial` into template globals
- **Jinja Extension**: `PartialsJinjaExtension` for declarative registration via Jinja2's extension system
- **Framework Integration**: Optional Flask and Starlette/FastAPI support with automatic renderer detection

The library works by registering a `render_partial` function in Jinja2's global namespace, which can then be called from within templates to render sub-templates with isolated data contexts.

## Framework Integrations

### Pure Jinja2
```python
from jinja2 import Environment, FileSystemLoader
import jinja_partials

# Method 1: Direct registration
env = Environment(loader=FileSystemLoader("templates"))
jinja_partials.register_environment(env, markup=False)

# Method 2: Extension-based (preferred)
env = Environment(
    loader=FileSystemLoader("templates"),
    extensions=["jinja_partials.PartialsJinjaExtension"]
)
```

### Flask Integration
```python
import flask
import jinja_partials

app = flask.Flask(__name__)
jinja_partials.register_extensions(app)
# render_partial now available in all templates
```

### FastAPI/Starlette Integration
```python
from fastapi.templating import Jinja2Templates
import jinja_partials

templates = Jinja2Templates("templates")
jinja_partials.register_starlette_extensions(templates)
```

## Testing Structure

- **Test Location**: All tests in `tests/` directory
- **Fixtures**: `conftest.py` provides fixtures for Flask, Starlette, and pure Jinja2 environments
- **Test Templates**: Located in `tests/test_templates/` with realistic partial examples
- **Test Categories**: Rendering functionality, framework integrations, error handling, markup behavior
- **Key Test Pattern**: Each framework integration gets its own fixture and test suite

## Key Files

- **`jinja_partials/__init__.py`**: Complete implementation - core API, registration functions, and Jinja extension
- **`tests/conftest.py`**: Test fixtures for all supported frameworks (Flask, Starlette, pure Jinja2)
- **`tests/test_rendering.py`**: Comprehensive test suite covering all functionality and edge cases
- **`tests/test_templates/`**: Template examples used for testing partial rendering
- **`example/app.py`**: Flask demo application showing real-world usage
- **`pyproject.toml`**: Hatchling-based build config with Python 3.8+ support
- **`ruff.toml`**: Linting configuration (E, F, I rules, 120 char line length, single quotes)
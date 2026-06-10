---
name: jinja-partials
description: >
  Simple reuse of partial HTML page templates in the Jinja template language for Python web frameworks. Use when writing Python code that uses the jinja_partials package.
license: MIT
compatibility: Requires Python >=3.10.
---

# Jinja Partials

Simple reuse of partial HTML page templates in the Jinja template language for Python web frameworks.

## Installation

```bash
pip install jinja-partials
```

## API overview

### Framework registration

Register render_partial with your web framework once at app startup.

- `register_extensions`: Register jinja_partials with a Flask application
- `register_fastapi_extensions`: Register jinja_partials with a FastAPI application
- `register_starlette_extensions`: Register jinja_partials with Starlette templates
- `register_quart_extensions`: Register jinja_partials with a Quart application
- `register_environment`: Register jinja_partials with a plain Jinja2 environment

### Rendering

Render partial templates directly or build framework-specific renderers.

- `render_partial`: Render a partial template and return the resulting HTML fragment
- `generate_render_partial`: Create a render_partial function bound to a specific renderer

### Jinja2 extension

Declarative registration via the Jinja2 extension mechanism.

- `PartialsJinjaExtension`: Jinja2 extension that automatically registers render_partial functionality

### Exceptions

Errors raised by jinja_partials.

- `PartialsException`: Raised when jinja_partials is misconfigured or a required web framework is not installed

## Resources

- [Full documentation](https://mkennedy.codes/docs/jinja-partials/)
- [llms.txt](llms.txt) — Indexed API reference for LLMs
- [llms-full.txt](llms-full.txt) — Comprehensive documentation for LLMs
- [Source code](https://github.com/mikeckennedy/jinja_partials)

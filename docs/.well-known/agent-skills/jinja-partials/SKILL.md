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

## When to use what

| Need | Use |
|------|-----|
| Flask app | `jinja_partials.register_extensions(app)` |
| Quart app | `jinja_partials.register_quart_extensions(app)` |
| FastAPI app | `jinja_partials.register_fastapi_extensions(app, templates)` |
| Starlette app | `jinja_partials.register_starlette_extensions(templates, app=app)` |
| Plain Jinja2 environment or unsupported framework | `jinja_partials.register_environment(env, markup=True)` |
| Declarative environment configuration | `Environment(extensions=['jinja_partials.PartialsJinjaExtension'])` |
| Custom render pipeline | `generate_render_partial(renderer) installed as a Jinja global` |

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

## Gotchas

1. register_starlette_extensions takes templates FIRST with app as an optional keyword — the argument order differs from register_fastapi_extensions(app, templates).
2. register_environment defaults markup=False while every other registration path uses markup=True; with autoescaping on, forgetting markup=True makes partials show up as escaped HTML text.
3. PartialsJinjaExtension on a Flask app renders partials through the Jinja environment, not flask.render_template — context processors, g, and request are unavailable inside partials; use register_extensions(app) if you need them.
4. render_partial with no renderer falls back to flask.render_template and raises PartialsException('No renderer specified') when Flask is not installed — pass a renderer or use generate_render_partial outside Flask.
5. Calling register_fastapi_extensions or register_starlette_extensions twice on the same app double-wraps the lifespan (no idempotency guard) — register exactly once at startup.
6. On an enable_async=True FastAPI/Starlette environment, render pages with await template.render_async(...) + HTMLResponse; templates.TemplateResponse(...) calls asyncio.run() inside the running event loop and crashes.

## Best practices

- Register once at app startup, before the app starts serving, so the partial-rendering executor is tied to the app's lifecycle.
- Pass app= to register_starlette_extensions when you have one — it upgrades from the shared module-level executor to a lifespan-managed one.
- Keep partials in templates/shared/partials/ and pass model data explicitly as keyword arguments; partials do not inherit the caller's context.
- Install as `pip install jinja-partials` (hyphen) but import as `jinja_partials` (underscore).

## End-to-end wiring

A complete, minimal Flask app — one registration call at startup, then `render_partial()` is available inside every template. Template paths are always given relative to the templates root.

```python
# app.py
import flask
import jinja_partials

app = flask.Flask(__name__)
jinja_partials.register_extensions(app)   # once, at startup


@app.get('/')
def index():
    return flask.render_template('home/index.html', videos=get_videos())
```

```html
<!-- templates/home/index.html -->
{% for v in videos %}
    {{ render_partial('shared/partials/video_square.html', video=v) }}
{% endfor %}
```

```html
<!-- templates/shared/partials/video_square.html — partials nest freely -->
<div>
    <a href="https://www.youtube.com/watch?v={{ video.id }}">
        {{ render_partial('shared/partials/video_image.html', video=video) }}
    </a>
    <div class="views">{{ "{:,}".format(video.views) }} views</div>
</div>
```

Other frameworks swap only the registration line: `register_quart_extensions(app)`, `register_fastapi_extensions(app, templates)`, `register_starlette_extensions(templates, app=app)`, or `register_environment(env, markup=True)` for a plain Jinja2 environment.

## Data flow is explicit (this is not `include`)

A partial sees **only** what you pass as keyword arguments to `render_partial` — there is no implicit sharing of the caller's context the way Jinja's `{% include %}` does it. That is the point: partials are functions over an explicit model, so renaming at the call site is normal:

```html
{% for v in videos %}
    {{ render_partial('shared/partials/video_square.html', video=v) }}  {# outer `v` becomes inner `video` #}
{% endfor %}
```

The one exception: on the Flask `register_extensions` path (and only there), partials render through `flask.render_template`, so Flask context processors, `g`, and `request` are also available inside partials.

## Project layout convention

Partials are ordinary Jinja templates; the convention is a `partials` subfolder under `templates/shared`:

```
templates/
├── home/
│   ├── index.html
│   └── listing.html
└── shared/
    ├── _layout.html          # normal Jinja {% extends %} layout — partials don't replace it
    └── partials/
        ├── video_image.html
        └── video_square.html
```

Partials complement, not replace, Jinja inheritance: pages still `{% extends 'shared/_layout.html' %}`; `render_partial` handles the reusable fragments inside those pages.

## Async apps: how it works and the one page-level rule

Quart/FastAPI/Starlette use `enable_async=True` Jinja environments, and Jinja expressions can't `await` — so registration installs a renderer that runs each partial's `render_async` on a small thread pool tied to the app's lifespan (`max_workers=4` by default, tunable on each `register_*` call). `{{ render_partial(...) }}` in templates needs no changes in async apps.

The page-level rule for FastAPI/Starlette with an async environment: render the **page** with `await template.render_async(...)` and return an `HTMLResponse` — partials inside it just work:

```python
@app.get('/')
async def index() -> HTMLResponse:
    template = templates.get_template('home/index.html')
    return HTMLResponse(await template.render_async(items=items))
```

## Custom renderers

Every registration path is sugar over `generate_render_partial(renderer)`, where `renderer(template_name, **data) -> str`. For an unsupported framework or a custom pipeline, bind your own:

```python
def renderer(template_name: str, **data) -> str:
    return my_env.get_template(template_name).render(**data)

my_env.globals.update(render_partial=jinja_partials.generate_render_partial(renderer))
```

## Fetching the docs as Markdown

Every page on the documentation site has a plain-Markdown twin: swap the `.html` extension for `.md` to get token-efficient source without the site chrome. For example https://mkennedy.codes/docs/jinja-partials/reference/render_partial.html is also available at https://mkennedy.codes/docs/jinja-partials/reference/render_partial.md. Prefer the `.md` form when reading these docs programmatically.


## Resources

- [Full documentation](https://mkennedy.codes/docs/jinja-partials/)
- [llms.txt](llms.txt) — Indexed API reference for LLMs
- [llms-full.txt](llms-full.txt) — Comprehensive documentation for LLMs
- [Source code](https://github.com/mikeckennedy/jinja_partials)

---
name: jinja-partials
description: Reusable HTML fragments for Jinja2 templates in Flask, Quart, FastAPI, Starlette, or any Jinja2 environment, through a render_partial() template global that renders a fragment file with explicitly passed data and nests freely. Use when adding jinja_partials or jinja-partials to an app, writing or refactoring templates that repeat markup, serving HTMX fragments, choosing between include, macro, and render_partial, or when a partial renders as escaped text, raises PartialsException or TemplateNotFound, or a FastAPI or Starlette route fails with "asyncio.run() cannot be called from a running event loop".
license: MIT
compatibility: Python 3.10 or newer; depends only on jinja2. Flask, Quart, FastAPI, and Starlette are optional and must be installed separately.
---

# jinja-partials

Repeated HTML fragments in Jinja2 templates are hard to keep consistent. jinja_partials adds a `render_partial(template_name, **data)` global that renders a fragment file with exactly the keyword arguments you pass, returns `markupsafe.Markup` so autoescaping leaves it alone, and nests. Misconfiguration raises `jinja_partials.PartialsException`; a bad template name raises `jinja2.TemplateNotFound`.

## Install

`uv add jinja-partials` or `pip install jinja-partials`. Import as `jinja_partials`. Install your web framework yourself; the library never pulls one in.

## Use

```python
import flask
import jinja_partials

app = flask.Flask(__name__)
jinja_partials.register_extensions(app)  # once, at startup, before serving
```

```html
{# templates/home/index.html #}
{% for v in videos %}
    {{ render_partial('shared/partials/video_square.html', video=v) }}  {# outer v becomes inner video #}
{% endfor %}
```

Other frameworks swap only the registration line (see the table). In a test, render a fragment directly: `templates.env.globals['render_partial']('shared/partials/card.html', item=item)`, or `jinja_partials.render_partial(name, **data)` inside a Flask request context.

## Rules

- A partial sees only the keyword arguments you pass it plus environment globals. It never inherits the caller's context the way `{% include %}` does; pass everything, and use `| default(...)` for optional inputs.
- Template names are paths relative to the templates root with forward slashes and the extension, as for `render_template`. Jinja's loader refuses names that leave that root (`..`, absolute paths); a custom renderer bound with `generate_render_partial` must refuse them itself. When a request chooses the partial, map its value to a name you wrote rather than building a path from it.
- `register_environment(env)` defaults to `markup=False`. With autoescaping on, that inserts the fragment as escaped text. Pass `markup=True`. Every other registration path and `PartialsJinjaExtension` already use `markup=True`.
- `register_starlette_extensions(templates, app=app)` takes templates first and app as a keyword. The FastAPI order is `register_fastapi_extensions(app, templates)`. Swapping them fails with `AttributeError: 'Starlette' object has no attribute 'env'`.
- Register once per app where it is built. A second `register_fastapi_extensions` or `register_starlette_extensions` call wraps the lifespan again, and a second Quart registration adds another pair of serving hooks. There is no idempotency guard.
- Only `register_extensions(app)` on Flask renders partials through `flask.render_template`, so only there do context processors and the `template_rendered` signal apply inside partials. `PartialsJinjaExtension` on a Flask app skips them, though `g`, `request`, and `session` remain available as environment globals.
- In FastAPI and Starlette with an `enable_async=True` environment, render the page with `await template.render_async(...)` and return `HTMLResponse`. `templates.TemplateResponse(...)` calls `asyncio.run()` inside the running loop and raises `RuntimeError`. Partials inside the page need no change.
- Partials in async apps render on a thread pool (`max_workers=4` default) and the caller blocks for the result. Nested partials render on their own thread and do not count against `max_workers`. Renders beyond the pool size queue; they do not fail. Nesting deeper than `MAX_NESTED_RENDERS` (100) raises `RecursionError`, the sign of a partial that renders itself.
- `render_partial` with no renderer falls back to `flask.render_template` and raises `PartialsException('No renderer specified')` when Flask is absent. Outside Flask, bind a renderer with `generate_render_partial`.
- Framework imports are optional; `register_*` raises `PartialsException('Install <Framework> to use ...')` when the framework is missing.

## Decision table

| Need | Use |
| --- | --- |
| Flask app | `jinja_partials.register_extensions(app)` |
| Quart app | `jinja_partials.register_quart_extensions(app, max_workers=4)` |
| FastAPI app | `jinja_partials.register_fastapi_extensions(app, templates, max_workers=4)` |
| Starlette app with lifespan-managed pool | `jinja_partials.register_starlette_extensions(templates, app=app, max_workers=4)` |
| Starlette templates, no app | `jinja_partials.register_starlette_extensions(templates)` (shared module pool) |
| Plain Jinja2 or unsupported framework | `jinja_partials.register_environment(env, markup=True)` |
| Declarative environment config | `Environment(extensions=['jinja_partials.PartialsJinjaExtension'])` |
| Custom render pipeline | `env.globals.update(render_partial=jinja_partials.generate_render_partial(renderer))` |
| Fragment response for HTMX | return the partial from the route with the framework's normal render call ([recipe](https://mkennedy.codes/docs/jinja-partials/user-guide/quickstart.html#hand-the-same-card-to-htmx)) |
| Flask context processors inside partials | `register_extensions(app)`, not the extension |

## API

- `render_partial(template_name, renderer=None, markup=True, **data) -> Markup | str`: the primitive. Raises `PartialsException` without a renderer when Flask is absent; raises `TemplateNotFound` for a bad name.
- `generate_render_partial(renderer, markup=True) -> Callable`: binds `renderer(template_name, **data) -> str`; install the result as the `render_partial` global.
- `register_extensions(app: Flask) -> None`: Flask; raises `PartialsException` if Flask is missing.
- `register_quart_extensions(app: Quart, max_workers=4) -> None`: Quart; pool created in `before_serving`, shut down in `after_serving`, stored in `app.extensions['jinja_partials_executor']`.
- `register_fastapi_extensions(app: FastAPI, templates: Jinja2Templates, max_workers=4) -> None`: wraps the lifespan; pool on `app.state.jinja_partials_executor`; an existing `lifespan=` keeps running.
- `register_starlette_extensions(templates: Jinja2Templates, app: Starlette | None = None, max_workers=4) -> None`: templates first; `max_workers` applies only with `app`.
- `register_environment(env: Environment, markup=False) -> None`: plain Jinja2, sync or async; pass `markup=True`.
- `PartialsJinjaExtension(environment)`: Jinja2 extension; calls `register_environment(environment, markup=True)`.
- `PartialsException(Exception)`: misconfiguration or missing framework.

## Output

Page template plus partial, and the rendered result:

```html
{# home/index.html #}            {# shared/partials/card.html #}
{% for item in items %}          <div class="card"><h3>{{ item.title }}</h3></div>
  {{ render_partial('shared/partials/card.html', item=item) }}
{% endfor %}
```

```html
<div class="card"><h3>Python Basics</h3></div>   <!-- correct: Markup inserted verbatim -->
&lt;div class="card"&gt;&lt;h3&gt;Python Basics&lt;/h3&gt;&lt;/div&gt;   <!-- escaped text: markup=False on register_environment -->
```

Fix order when something is wrong: confirm the registration call ran once at startup, then the template path, then that every variable the fragment reads was passed, then `markup=True` on the plain Jinja2 path, then the page-level `render_async` rule in async apps.

## Resources

- Documentation: <https://mkennedy.codes/docs/jinja-partials/>
- Frameworks: <https://mkennedy.codes/docs/jinja-partials/user-guide/frameworks.html>
- Troubleshooting: <https://mkennedy.codes/docs/jinja-partials/user-guide/troubleshooting.html>
- How it works: <https://mkennedy.codes/docs/jinja-partials/user-guide/how-it-works.html>
- API reference: <https://mkennedy.codes/docs/jinja-partials/reference/>
- llms.txt: <https://mkennedy.codes/docs/jinja-partials/llms.txt>
- llms-full.txt: <https://mkennedy.codes/docs/jinja-partials/llms-full.txt>
- Source: <https://github.com/mikeckennedy/jinja_partials>

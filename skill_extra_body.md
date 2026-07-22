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

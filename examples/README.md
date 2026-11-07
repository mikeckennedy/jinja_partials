# Example apps

The same idea, built four times. Each folder is a small, runnable web app that registers jinja_partials with one framework and renders a page out of nested partials. The templates are the part worth diffing, because they are the part that does not change.

| App | Run it | Port | What you get |
| --- | --- | --- | --- |
| [example_flask](example_flask/) | `python examples/example_flask/app.py` | 5001 | The full video site behind the README screenshot: a layout, two pages, a JSON database, and the `video_square` and `video_image` partials |
| [example_quart](example_quart/) | `python examples/example_quart/app.py` | 10001 | Cards with nested badges, rendered through Quart's `before_serving` and `after_serving` hooks |
| [example_starlette](example_starlette/) | `python examples/example_starlette/app.py` | 10002 | The same cards and badges on an `enable_async=True` environment with lifespan-managed rendering |
| [example_fastapi](example_fastapi/) | `python examples/example_fastapi/app.py` | 10003 | The same cards and badges on FastAPI, with the lifespan wrapped by `register_fastapi_extensions` |

Each app has its own `requirements.txt`. Install it into whatever environment you like, then run the app from the repository root with the command in the table:

```bash
pip install -r examples/example_fastapi/requirements.txt
python examples/example_fastapi/app.py
```

The three async apps are deliberately near-identical. Their `card.html` partials are byte-for-byte the same file, and each card renders a `badge.html` partial inside itself, so every page load exercises a nested partial on the thread pool described in [How it works](https://mkennedy.codes/docs/jinja-partials/user-guide/how-it-works.html). Notice that the FastAPI and Starlette routes render their page with `await template.render_async(...)` and return an `HTMLResponse`; that is [the page-level rule](https://mkennedy.codes/docs/jinja-partials/user-guide/frameworks.html#the-page-level-rule-for-async-environments) for async environments, and a `TemplateResponse` there would fail.

The Flask folder also holds `example_use_jinja_partials.py`, a script with no web server at all. It builds a Jinja2 environment from an in-memory dictionary of templates, enables `PartialsJinjaExtension` declaratively, and prints the rendered result, which is the quickest way to watch `render_partial` work without starting anything.

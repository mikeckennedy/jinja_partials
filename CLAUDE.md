# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

jinja_partials (PyPI: `jinja-partials`) is a small, fully typed Python library that adds a `render_partial()` global to Jinja2 templates so HTML fragments ("partials") can be composed and nested with explicitly passed data. It works with plain Jinja2 and has first-class registration helpers for Flask, Quart, FastAPI, and Starlette. Requires Python >= 3.10; the only runtime dependency is `jinja2`.

The entire library is one module: `jinja_partials/__init__.py`, plus the empty `py.typed` marker (PEP 561) that must remain in the package and ship in the wheel.

## Commands

The project virtualenv is `venv/` (not `.venv/`) and is uv-managed — it has **no pip**. Use `uv pip ...` for installs; tools live in `venv/bin/`.

```bash
venv/bin/pytest                                # run the test suite (all tests live in tests/test_rendering.py)
venv/bin/pytest tests/test_rendering.py::test_render_with_data   # run a single test by node id
ruff check . && ruff format .                  # lint + format (ruff.toml: 120 cols, single quotes, rules E/F/I)
uv build                                       # build sdist/wheel via hatchling (`python -m build` fails: build pkg not installed)
uv pip install -r requirements-development.txt # install dev deps (pytest, all four frameworks, great-docs)
venv/bin/python scripts/build_docs.py          # build the docs site into docs/ (the default VS Code build task)
venv/bin/python scripts/serve_docs.py          # preview committed docs/ at http://127.0.0.1:8099/docs/jinja-partials/
```

Dependency changes: edit the `.piptools` source files (`requirements.piptools` = runtime, `requirements-development.piptools` = dev), then recompile the pinned lockfiles — never hand-edit the compiled `.txt` files:

```bash
uv pip compile requirements-development.piptools --output-file requirements-development.txt --exclude-newer "1 week"
```

pytest config (`pytest.ini`) runs strict: `--strict-markers --strict-config`, and `filterwarnings = error` — any warning other than `UserWarning`/`DeprecationWarning` fails the suite, and new markers must be declared in the ini.

## Architecture

### Layering: one primitive, framework adapters around it

- `render_partial(template_name, renderer=None, markup=True, **data)` is the core primitive. With no renderer it falls back to `flask.render_template`, raising `PartialsException` if Flask isn't installed.
- `generate_render_partial(renderer, markup=...)` is just `functools.partial(render_partial, ...)` binding a renderer.
- Every `register_*` function builds a framework-specific synchronous `renderer(template_name, **data) -> str` closure and installs it as a Jinja global via `env.globals.update(render_partial=generate_render_partial(renderer, ...))`. Templates then call `{{ render_partial('shared/partials/x.html', model=value) }}`, including nested/recursive partials.
- Registration paths: `register_extensions(app)` (Flask), `register_quart_extensions(app)`, `register_fastapi_extensions(app, templates)`, `register_starlette_extensions(templates, app=None)` (note: templates first, app as keyword), `register_environment(env)` (plain Jinja2), and the declarative `PartialsJinjaExtension` (`Environment(extensions=[...])`).
- Only the Flask `register_extensions` path renders through `flask.render_template`, so Flask context processors, `g`, and `request` are available inside partials there and **nowhere else** (including the `PartialsJinjaExtension` path on a Flask app).
- `markup` defaults differ by design: `render_partial`/`generate_render_partial` default `markup=True`, `register_environment` defaults `markup=False`, and all framework paths plus `PartialsJinjaExtension` hardcode `markup=True`. The `@overload` sets encode this (`Literal[True] -> Markup`, `Literal[False] -> str`) — changing a default is a typed behavior break.

### Async rendering: the executor machinery

Jinja template expressions cannot `await`, but Quart/FastAPI/Starlette use `enable_async=True` environments. The bridge: the renderer submits `asyncio.run(template.render_async(**data))` to a `ThreadPoolExecutor` worker thread (fresh event loop) and blocks on `future.result()`. This block-in-place is the accepted tradeoff — do not "fix" it by making the renderer async.

Three executor tiers:
1. A **dedicated executor** created inside the app's lifespan: FastAPI/Starlette wrap `app.router.lifespan_context` (executor stored on `app.state.jinja_partials_executor`); Quart uses `before_serving`/`after_serving` (stored in `app.extensions['jinja_partials_executor']`).
2. A lazy per-registration **fallback executor** (closure variable) for renders outside a serving cycle — intentionally never shut down.
3. A module-level `_async_render_executor` used by `register_environment` / `PartialsJinjaExtension` / app-less Starlette — also intentionally never shut down.

Lifecycle invariants to preserve (from "exception-safe and re-entrant" work, commit 20c0e11):
- The dedicated executor is created inside the lifespan wrapper and shut down in a `finally`, so failed startups still clean up and the app can start/stop repeatedly (e.g. multiple `TestClient` cycles).
- App state is cleared to `None` **before** `executor.shutdown(wait=True)` so concurrent renders fall back instead of submitting to a dying pool. Executor lookup is `... or fallback_executor` — truthiness — so the cleared sentinel must stay `None`.
- Quart's `before_serving` self-heals a stale executor left by a previously failed startup (a failed startup skips `after_serving`).
- Calling `register_fastapi_extensions`/`register_starlette_extensions` twice on one app double-wraps the lifespan — there is no idempotency guard.

### Optional dependencies and typing

- Frameworks are imported in `try/except ImportError` blocks with the module name set to `None` on failure; runtime checks raise `PartialsException`. Real framework types appear only under `if TYPE_CHECKING:` and are string-quoted in signatures. Never add a top-level framework import.
- Exactly two `# type: ignore` comments are load-bearing (the `yield state if state else {}` lines in the lifespan wrappers). No type-checker config exists in the repo — the typing contract is full inline annotations + `py.typed` — so don't introduce blanket ignores or invent strictness config.
- Versioning: the static `version` in `pyproject.toml` is the source of truth (there is no setup.py); `__version__` resolves via `importlib.metadata` at runtime. Releases get a `change-log.md` entry (Keep a Changelog format, `## [X.Y.Z] - YYYY-MM-DD`) and a `vX.Y.Z` git tag.
- Ruff's `target-version` is py313 while `requires-python` is >=3.10 — don't let suggested fixes introduce 3.11+ syntax into shipped code.

### Tests

- One test file (`tests/test_rendering.py`) with fixtures in `tests/conftest.py` (a Flask app in a test request context, a Starlette `Jinja2Templates` setup, and a plain Jinja environment — all over `tests/test_templates/`).
- There is **no pytest-asyncio and no async test functions**. Async behavior (lifespans, `enable_async` environments) is driven with `asyncio.run(...)` inside plain sync tests — follow that pattern; an `async def test_` will not run as expected.
- Executor lifecycle tests monkeypatch `jinja_partials.ThreadPoolExecutor` with a recording subclass (`_track_executors`) — that's the seam into threading internals.
- Two tests simulate missing frameworks by mutating `sys.modules` and re-importing `jinja_partials` mid-suite.

### Docs pipeline (Great Docs / Quarto)

Sources are `README.md`, `change-log.md`, and the library docstrings, configured by hand-edited `great-docs.yml`. `scripts/build_docs.py` runs `great-docs build` into the ephemeral, fully gitignored `great-docs/` dir, mirrors `great-docs/_site/` into the **committed** `docs/` folder, then runs `scripts/postprocess_site.py`. The site deploys to https://mkennedy.codes/docs/jinja-partials/ via git push + server-side git pull.

- **Never hand-edit `docs/`** — it is generated output, deleted and rebuilt wholesale on every build. **Never edit anything under `great-docs/`** either. Content changes go in README.md, docstrings, change-log.md, or great-docs.yml; HTML output corrections go in `scripts/postprocess_site.py`.
- `scripts/postprocess_site.py` patches known Great Docs 0.13 output bugs and prints per-fix counts — after a Great Docs upgrade, watch for counts dropping to 0 (fix may be removable) or new breakage.
- `scripts/fix_readme_code_comments.py` is a Quarto pre-render hook (wired in `great-docs.yml`) that repairs `#` comments inside README code fences after heading demotion — removing it silently corrupts Python examples on the docs homepage.
- Preview with `scripts/serve_docs.py` (serves under the production `/docs/jinja-partials/` subpath); a plain `http.server` in `docs/` will 404 on assets.
- Keep `seo.canonical.base_url` set and `mcp.enabled: false` in `great-docs.yml` (auto-detection points canonicals at the wrong domain; enabling MCP renders an empty tab).

### Examples

`examples/` holds four parallel demo apps, each runnable directly: Flask (`python examples/example_flask/app.py`, port 5001 — the full demo behind the README screenshots), Quart (10001), Starlette (10002), FastAPI (10003). The async three all render through `enable_async=True` environments and exercise the executor path. The FastAPI/Starlette examples build an explicit `jinja2.Environment` and render pages via `await template.render_async(...)` + `HTMLResponse` — on an async environment, `templates.TemplateResponse(...)` would call `template.render()` → `asyncio.run()` inside the running event loop and crash; partials inside the page still render synchronously via the app-managed executor.

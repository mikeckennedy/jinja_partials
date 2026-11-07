# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.4.0] - 2026-11-06

### Fixed

- Nested partials in async apps (Quart, FastAPI, Starlette, and async Jinja2 environments) no longer deadlock the render thread pool. A nested `render_partial` call used to wait on the same pool its outer partial was occupying, so nesting as deep as `max_workers`, or enough concurrent requests with nested partials, hung every request. Nested renders now run on their own short-lived thread, and nesting depth no longer counts against `max_workers`.
- A partial that renders itself, or a cycle of partials, in an async environment (Quart, FastAPI, Starlette, or `enable_async=True` Jinja2) now raises `RecursionError` at `MAX_NESTED_RENDERS` (100) levels, as a sync environment already did on its own. Each nested async render runs on its own thread with its own event loop, so Python's recursion limit never applied; the render kept creating threads, each slower than the last and holding file descriptors, until the process ran out.

### Added

- Regression tests that names leaving the templates folder (`..` segments, leading whitespace, absolute paths, backslashes, directory names) raise `TemplateNotFound` on every registration path. Jinja's loader already refused them; the tests pin that the built-in renderers pass names to it untouched.

### Documentation

- Added a user guide to the documentation site: why partials, installation, quickstart, frameworks, troubleshooting, testing, how it works, and FAQ. The guide pages are included in `llms-full.txt`.
- Replaced the generated agent skill with a hand-written `skills/jinja-partials/SKILL.md` that documents the rules of the package (explicit data flow, markup defaults, Starlette argument order, the async page-level rule, registration once) rather than only its API names.
- Every public name now has an example in its docstring, and the module docstring names the entry points.
- Corrected the note about `PartialsJinjaExtension` on Flask: only context processors and the `template_rendered` signal are skipped inside partials; `g`, `request`, and `session` remain available.
- Corrected the README note about older Python versions: 0.3.0 already had synchronous Starlette support.
- `scripts/build_docs.py` now fails when `llms.txt`, `llms-full.txt`, or the skill files are missing from the build output, or when `llms-full.txt` has no user guide section.
- The docs now build with great-docs 0.17.0 (the dev lockfile was recompiled from 0.13.0), and `scripts/postprocess_site.py` repairs two more output bugs: the `**data` parameter rendered as `data: Any = {}` in the `render_partial` signatures, and parameter defaults wrapped in nested backticks in the Markdown reference companions.
- `generate_render_partial` now says that a custom renderer is responsible for refusing names that leave its templates folder, and the user guide explains how to let a request choose a partial safely (map the value to a name you wrote).

## [0.3.2] - 2026-06-11

### Fixed

- Async executor lifecycle is now exception-safe and re-entrant. Apps registered with `register_fastapi_extensions`, `register_starlette_extensions`, or `register_quart_extensions` can now start and stop repeatedly (e.g. multiple `TestClient` cycles) without failing, and an exception during a wrapped lifespan no longer leaks the executor (#14).
- Renders that happen outside a lifespan/serving cycle now use a lazy per-registration fallback executor that honors `max_workers`, instead of degrading to a shared 4-worker pool.

### Changed

- The FastAPI and Starlette example apps now use `enable_async=True` environments and render pages via `render_async`, exercising the executor lifecycle.
- Added more package keywords (Jinja, HTMX, components, fragments, and the supported frameworks) for better PyPI discoverability.

## [0.3.1] - 2026-01-28

### Added

- `register_quart_extensions(app, max_workers)` - Lifecycle-managed registration for Quart apps
- `register_fastapi_extensions(app, templates, max_workers)` - Lifecycle-managed registration for FastAPI apps
- Updated `register_starlette_extensions(templates, app, max_workers)` - Optional app parameter for lifecycle management
- Example apps for FastAPI, Starlette, and Quart in `examples/` directory

### Fixed

- Async rendering now works with Quart, FastAPI, and Starlette frameworks
- Fixed "asyncio.run() cannot be called from a running event loop" error when using `render_partial` in async environments
- Templates compiled with `enable_async=True` now render correctly via ThreadPoolExecutor

### Changed

- Minimum Python version is now 3.10
- Version info now uses package metadata instead of hardcoded value
- Reorganized examples: `example/` renamed to `examples/` with multiple framework examples

## [0.3.0] - 2025-05-31

### Added

- `PartialsJinjaExtension`, a Jinja2 extension for declarative registration: `Environment(extensions=['jinja_partials.PartialsJinjaExtension'])` makes `render_partial` available with markup enabled. Thanks to @jenisys.
- `__version__` is now included in `__all__`.
- An example of using `register_environment` with a plain Jinja2 environment, and README docs for it.
- More tests, and a `pytest.ini` so the suite runs with a bare `pytest`.

### Changed

- Packaging moved to `pyproject.toml`. `setup.py` is kept for Conda builds.
- `generate_render_partial` is now annotated as returning `Markup | str`, matching its `markup` argument.

### Fixed

- The demo app works with Pydantic 2.

## [0.2.1] - 2024-04-12

### Fixed

- `setup.py` now declares the `jinja2` dependency in `install_requires` instead of reading it from `requirements.txt`, so Conda packaging works ([#9](https://github.com/mikeckennedy/jinja_partials/issues/9)).

### Added

- An optional `pyproject.toml` for building with Hatch.

## [0.2.0] - 2024-02-01

### Added

- `register_environment(env, markup=False)` adds `render_partial` to any Jinja2 `Environment`, so partials work outside a web framework ([#4](https://github.com/mikeckennedy/jinja_partials/issues/4), [#6](https://github.com/mikeckennedy/jinja_partials/pull/6)). Thanks to @sam-kleiner.
- A `markup` argument on `render_partial` and `generate_render_partial` (default `True`). Pass `False` to get a plain `str` instead of `Markup`.

### Changed

- The project is formatted and linted with Ruff.

## [0.1.1] - 2021-12-14

### Added

- Framework-agnostic rendering: `render_partial` accepts a `renderer` callable, and `generate_render_partial(renderer)` binds one. Flask is no longer required.
- `register_starlette_extensions(templates)` for Starlette and FastAPI ([#2](https://github.com/mikeckennedy/jinja_partials/pull/2)). Thanks to @vrslev.
- A test suite.
- README discussion of how partials compare with Jinja's `include` and `macro`.

## [0.1.0] - 2021-07-26

### Added

- First release: the `render_partial()` Jinja global and `register_extensions(app)` for Flask, with a demo app.

[0.4.0]: https://github.com/mikeckennedy/jinja_partials/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/mikeckennedy/jinja_partials/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/mikeckennedy/jinja_partials/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/mikeckennedy/jinja_partials/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/mikeckennedy/jinja_partials/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/mikeckennedy/jinja_partials/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/mikeckennedy/jinja_partials/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/mikeckennedy/jinja_partials/releases/tag/v0.1.0

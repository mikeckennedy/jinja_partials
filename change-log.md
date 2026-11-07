# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.4.0] - 2026-11-06

### Fixed

- Nested partials in async apps (Quart, FastAPI, Starlette, and async Jinja2 environments) no longer deadlock the render thread pool. A nested `render_partial` call used to wait on the same pool its outer partial was occupying, so nesting as deep as `max_workers`, or enough concurrent requests with nested partials, hung every request. Nested renders now run on their own short-lived thread, and nesting depth no longer counts against `max_workers`.

### Documentation

- Added a user guide to the documentation site: why partials, installation, quickstart, frameworks, troubleshooting, testing, how it works, and FAQ. The guide pages are included in `llms-full.txt`.
- Replaced the generated agent skill with a hand-written `skills/jinja-partials/SKILL.md` that documents the rules of the package (explicit data flow, markup defaults, Starlette argument order, the async page-level rule, registration once) rather than only its API names.
- Every public name now has an example in its docstring, and the module docstring names the entry points.
- Corrected the note about `PartialsJinjaExtension` on Flask: only context processors and the `template_rendered` signal are skipped inside partials; `g`, `request`, and `session` remain available.
- Corrected the README note about older Python versions: 0.3.0 already had synchronous Starlette support.
- `scripts/build_docs.py` now fails when `llms.txt`, `llms-full.txt`, or the skill files are missing from the build output, or when `llms-full.txt` has no user guide section.
- The docs now build with great-docs 0.17.0 (the dev lockfile was recompiled from 0.13.0), and `scripts/postprocess_site.py` repairs two more output bugs: the `**data` parameter rendered as `data: Any = {}` in the `render_partial` signatures, and parameter defaults wrapped in nested backticks in the Markdown reference companions.

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

## [0.3.0] - Previous release

See [GitHub releases](https://github.com/mikeckennedy/jinja_partials/releases) for earlier history.

[0.4.0]: https://github.com/mikeckennedy/jinja_partials/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/mikeckennedy/jinja_partials/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/mikeckennedy/jinja_partials/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/mikeckennedy/jinja_partials/releases/tag/v0.3.0

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

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

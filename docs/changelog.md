# Changelog

This changelog is generated automatically from [GitHub Releases](https://github.com/mikeckennedy/jinja_partials/releases).


# v0.3.2

*2026-06-11* · [GitHub](https://github.com/mikeckennedy/jinja_partials/releases/tag/v0.3.2)


## \[0.3.2\] - 2026-06-11


### Fixed

- Async executor lifecycle is now exception-safe and re-entrant. Apps registered with [register_fastapi_extensions](reference/register_fastapi_extensions.html#jinja_partials.register_fastapi_extensions), [register_starlette_extensions](reference/register_starlette_extensions.html#jinja_partials.register_starlette_extensions), or [register_quart_extensions](reference/register_quart_extensions.html#jinja_partials.register_quart_extensions) can now start and stop repeatedly (e.g. multiple `TestClient` cycles) without failing, and an exception during a wrapped lifespan no longer leaks the executor ([\#14](https://github.com/mikeckennedy/jinja_partials/issues/14)).
- Renders that happen outside a lifespan/serving cycle now use a lazy per-registration fallback executor that honors `max_workers`, instead of degrading to a shared 4-worker pool.


### Changed

- The FastAPI and Starlette example apps now use `enable_async=True` environments and render pages via `render_async`, exercising the executor lifecycle.
- Added more package keywords (Jinja, HTMX, components, fragments, and the supported frameworks) for better PyPI discoverability.


# v0.3.1

*2026-01-28* · [GitHub](https://github.com/mikeckennedy/jinja_partials/releases/tag/v0.3.1)


## \[0.3.1\] - 2026-01-28


### Added

- `register_quart_extensions(app, max_workers)` - Lifecycle-managed registration for Quart apps
- `register_fastapi_extensions(app, templates, max_workers)` - Lifecycle-managed registration for FastAPI apps
- Updated `register_starlette_extensions(templates, app, max_workers)` - Optional app parameter for lifecycle management
- Example apps for FastAPI, Starlette, and Quart in `examples/` directory


### Fixed

- Async rendering now works with Quart, FastAPI, and Starlette frameworks
- Fixed "asyncio.run() cannot be called from a running event loop" error when using [render_partial](reference/render_partial.html#jinja_partials.render_partial) in async environments
- Templates compiled with `enable_async=True` now render correctly via ThreadPoolExecutor


### Changed

- Minimum Python version is now 3.10
- Version info now uses package metadata instead of hardcoded value
- Reorganized examples: `example/` renamed to `examples/` with multiple framework examples


# v0.3.0

*2025-05-31* · [GitHub](https://github.com/mikeckennedy/jinja_partials/releases/tag/v0.3.0)

Jinja_Partials Release Notes

**Since 285d147a (15 commits)**


## 🚀 New Features

- **PartialsJinjaExtension**: Added a declarative Jinja2 extension for easy integration of partials and templates. Thank you [<span class="citation" cites="jenisys">@jenisys</span>](https://github.com/jenisys)!
- **Versioning**: Enhanced the `__all__` import list to include version information, making it easier to manage updates.


## 🔧 Improvements

- **Code Cleanup**: Cleaned up code and fixed lint warnings on test files.
- **Workspace Setup**: Added a workspace in Visual Studio Code for better type checking and navigation.


## 📚 Documentation

- Added new environment feature and how to use it with Flask.


## 🔒 Security

- No security-related changes were made during this release.


## 🏗️ Infrastructure

- No infrastructure improvements or changes were made in this release.


# v0.2.1

*2024-04-12* · [GitHub](https://github.com/mikeckennedy/jinja_partials/releases/tag/v0.2.1)

Solves [\#9](https://github.com/mikeckennedy/jinja_partials/issues/9) requirements.txt details not added to `setup.py`.


# v0.2.0

*2024-02-02* · [GitHub](https://github.com/mikeckennedy/jinja_partials/releases/tag/v0.2.0)

This release adds a `register_environment(environment)` method to allow using partials with Jinja outside of a web framework like Flask. See [\#4](https://github.com/mikeckennedy/jinja_partials/issues/4) for details. Thank you to [<span class="citation" cites="sam-kleiner">@sam-kleiner</span>](https://github.com/sam-kleiner) for this feature.

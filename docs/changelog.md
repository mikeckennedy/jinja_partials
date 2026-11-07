# Changelog

This changelog is generated automatically from [GitHub Releases](https://github.com/mikeckennedy/jinja_partials/releases).


# v0.4.0

*2026-11-07* · [GitHub](https://github.com/mikeckennedy/jinja_partials/releases/tag/v0.4.0)


## \[0.4.0\] - 2026-11-06


### Fixed

- Nested partials in async apps (Quart, FastAPI, Starlette, and async Jinja2 environments) no longer deadlock the render thread pool. A nested [render_partial](reference/render_partial.html#jinja_partials.render_partial) call used to wait on the same pool its outer partial was occupying, so nesting as deep as `max_workers`, or enough concurrent requests with nested partials, hung every request. Nested renders now run on their own short-lived thread, and nesting depth no longer counts against `max_workers`.
- A partial that renders itself, or a cycle of partials, in an async environment (Quart, FastAPI, Starlette, or `enable_async=True` Jinja2) now raises `RecursionError` at `MAX_NESTED_RENDERS` (100) levels, as a sync environment already did on its own. Each nested async render runs on its own thread with its own event loop, so Python's recursion limit never applied; the render kept creating threads, each slower than the last and holding file descriptors, until the process ran out.


### Added

- Regression tests that names leaving the templates folder (`..` segments, leading whitespace, absolute paths, backslashes, directory names) raise `TemplateNotFound` on every registration path. Jinja's loader already refused them; the tests pin that the built-in renderers pass names to it untouched.


### Documentation

- Added a user guide to the documentation site: why partials, installation, quickstart, frameworks, troubleshooting, testing, how it works, and FAQ. The guide pages are included in `llms-full.txt`.
- Replaced the generated agent skill with a hand-written `skills/jinja-partials/SKILL.md` that documents the rules of the package (explicit data flow, markup defaults, Starlette argument order, the async page-level rule, registration once) rather than only its API names.
- Every public name now has an example in its docstring, and the module docstring names the entry points.
- Corrected the note about [PartialsJinjaExtension](reference/PartialsJinjaExtension.html#jinja_partials.PartialsJinjaExtension) on Flask: only context processors and the `template_rendered` signal are skipped inside partials; `g`, `request`, and `session` remain available.
- Corrected the README note about older Python versions: 0.3.0 already had synchronous Starlette support.
- `scripts/build_docs.py` now fails when `llms.txt`, `llms-full.txt`, or the skill files are missing from the build output, or when `llms-full.txt` has no user guide section.
- The docs now build with great-docs 0.17.0 (the dev lockfile was recompiled from 0.13.0), and `scripts/postprocess_site.py` repairs two more output bugs: the `**data` parameter rendered as `data: Any = {}` in the [render_partial](reference/render_partial.html#jinja_partials.render_partial) signatures, and parameter defaults wrapped in nested backticks in the Markdown reference companions.
- [generate_render_partial](reference/generate_render_partial.html#jinja_partials.generate_render_partial) now says that a custom renderer is responsible for refusing names that leave its templates folder, and the user guide explains how to let a request choose a partial safely (map the value to a name you wrote).


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


# v0.1.1

*2026-11-07* · [GitHub](https://github.com/mikeckennedy/jinja_partials/releases/tag/v0.1.1)

Published to PyPI on 2021-12-14.

- The package is now framework-agnostic: [render_partial](reference/render_partial.html#jinja_partials.render_partial) and [generate_render_partial](reference/generate_render_partial.html#jinja_partials.generate_render_partial) accept a custom renderer, and Flask is no longer required.
- Added FastAPI / Starlette support with a usage example in the README ([\#2](https://github.com/mikeckennedy/jinja_partials/issues/2), thanks [<span class="citation" cites="vrslev">@vrslev</span>](https://github.com/vrslev)).
- Added a test suite for the library.
- README: discussion of how partials compare with Jinja's `include` and `macro`.

*This GitHub release was created after the fact to match the version on [PyPI](https://pypi.org/project/jinja-partials/0.1.1/).*


# v0.1.0

*2026-11-07* · [GitHub](https://github.com/mikeckennedy/jinja_partials/releases/tag/v0.1.0)

Initial release of jinja-partials, published to PyPI on 2021-07-26.

- Adds the [render_partial()](reference/render_partial.html#jinja_partials.render_partial) Jinja global, so HTML fragments can be composed and nested with explicitly passed data.
- Flask integration via `jinja_partials.register_extensions(app)`.
- Includes a Flask demo app.

*This GitHub release was created after the fact to match the version on [PyPI](https://pypi.org/project/jinja-partials/0.1.0/).*

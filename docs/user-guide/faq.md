# FAQ

Short answers to the questions that come up most. Each links to the page with the full explanation.


# Why not just use include or macro?

They are close, and each falls short differently. `{% include %}` passes the whole caller context implicitly, so a fragment's inputs are invisible at the call site. `{% macro %}` has explicit parameters but must be imported into every page and is not a file you can render on its own. [Why partials](why-partials.md) has the longer version, and [issue \#1](https://github.com/mikeckennedy/jinja_partials/issues/1) has the original discussion.


# Does this work with HTMX?

Yes, and it is a good fit. A partial is an ordinary template, so a route can return it directly for an `hx-get` swap with `flask.render_template('shared/partials/video_square.html', video=v)`, while pages keep rendering the same fragment inline with [render_partial](../reference/render_partial.md#jinja_partials.render_partial).


# Can a partial extend a layout?

Yes. A partial is rendered like any other template, so `{% extends %}`, `{% block %}`, `{% include %}`, and macros all work inside it. The library's tests render a partial that extends a layout.


# Can I call render_partial from Python?

Yes. In a Flask request context, `jinja_partials.render_partial(name, **data)` uses `flask.render_template`. For other frameworks, the bound function is the [render_partial](../reference/render_partial.md#jinja_partials.render_partial) global on the environment: `templates.env.globals['render_partial'](name, **data)`. [Testing partials](testing.md) shows both.


# What does a partial see?

Only the keyword arguments you pass to [render_partial](../reference/render_partial.md#jinja_partials.render_partial), plus the environment's globals. On the Flask [register_extensions](../reference/register_extensions.md#jinja_partials.register_extensions) path, context processors, `g`, `request`, and `session` are also applied, because partials render through `flask.render_template` there.


# Why is my fragment escaped?

[render_partial](../reference/render_partial.md#jinja_partials.render_partial) returned a `str` instead of `Markup`. On the plain Jinja2 path pass `markup=True` to [register_environment](../reference/register_environment.md#jinja_partials.register_environment). See [Troubleshooting](troubleshooting.md#the-partial-shows-up-as-text-not-html).


# Do my templates change for async apps?

No. `{ render_partial(...) }` is identical in Quart, FastAPI, and Starlette. The one change is at the page level in FastAPI and Starlette: render pages with `await template.render_async(...)` and return an `HTMLResponse` when the environment has `enable_async=True`. See [Frameworks](frameworks.md#the-page-level-rule-for-async-environments).


# Is the thread pool safe to use under load?

Yes. Each top-level partial render takes one worker while it runs and queues when the pool is full. Nested partials render on their own thread, so nesting depth cannot exhaust the pool. The pool is created when the app starts serving and shut down when it stops, including after a failed startup. [How it works](how-it-works.md) describes the tiers.


# What happens if I register twice?

On Flask and plain Jinja2 the second call simply replaces the global. On FastAPI and Starlette each call wraps the lifespan again and on Quart each call adds another pair of serving hooks, so register once, where the app is built.


# Is there a version for other template languages?

For Pyramid and Chameleon, see [chameleon_partials](https://github.com/mikeckennedy/chameleon_partials).


# Which Python versions are supported?

3.10 and newer. See [Installation](installation.md).

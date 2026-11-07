# FAQ

Short answers, each with a link to the page that has the long one.


# Why not just use include or macro?

Because each is nearly right in a different way. `{% include %}` hands the fragment the entire caller context, so nothing at the call site says what the fragment reads. `{% macro %}` has proper parameters but must be imported into every page and is not a file you can render on its own. [Why partials](why-partials.md) tells the story, and [issue \#1](https://github.com/mikeckennedy/jinja_partials/issues/1) has the original debate.


# Does this work with HTMX?

It is a natural pairing. A partial is an ordinary template, so a route can return it directly for an `hx-get` swap with `flask.render_template('shared/partials/video_square.html', video=v)`, while your pages keep rendering the very same file inline with [render_partial](../reference/render_partial.md#jinja_partials.render_partial). One card, two delivery routes. The [Quickstart](quickstart.md#hand-the-same-card-to-htmx) ends with a worked example: cards that refresh their own view counts.


# Can a partial extend a layout?

Yes. A partial is rendered like any other template, so `{% extends %}`, `{% block %}`, `{% include %}`, and macros all work inside it. The library's test suite renders a partial that extends a layout, mostly to prove nobody accidentally forbids it.


# Can I call render_partial from Python?

Yes, and it is the best way to test one. In a Flask request context, `jinja_partials.render_partial(name, **data)` goes through `flask.render_template`. For the other frameworks, the bound function is the [render_partial](../reference/render_partial.md#jinja_partials.render_partial) global on the environment: `templates.env.globals['render_partial'](name, **data)`. [Testing partials](testing.md) shows both.


# What does a partial see?

Only the keyword arguments you passed, plus the environment's globals. On the Flask [register_extensions](../reference/register_extensions.md#jinja_partials.register_extensions) path, context processors, `g`, `request`, and `session` are applied too, because partials render through `flask.render_template` there. Everywhere else, if you did not pass it, it is not there, by design.


# Can a request choose which partial renders?

Not directly. The built-in renderers pass the name to Jinja's loader, which refuses `..` segments and absolute paths, so `render_partial(f'cards/{slug}.html')` cannot reach outside the templates folder. It can still reach any template inside it, though, so map the request value to names you wrote: `PARTIALS = {'card': 'cards/card.html', 'row': 'cards/row.html'}` and `render_partial(PARTIALS[kind], ...)`. A custom renderer built with [generate_render_partial](../reference/generate_render_partial.md#jinja_partials.generate_render_partial) gets no checking from the library; see [How it works](how-it-works.md#one-primitive-and-some-sugar).


# Why is my fragment escaped?

[render_partial](../reference/render_partial.md#jinja_partials.render_partial) returned a `str` instead of `Markup`. On the plain Jinja2 path, pass `markup=True` to [register_environment](../reference/register_environment.md#jinja_partials.register_environment). [Troubleshooting](troubleshooting.md#the-partial-shows-up-as-text-not-html) has the details.


# Do my templates change for async apps?

No. `{ render_partial(...) }` is identical in Quart, FastAPI, and Starlette. The one change is at the page level in FastAPI and Starlette: render pages with `await template.render_async(...)` and return an `HTMLResponse` when the environment has `enable_async=True`. See [the page-level rule](frameworks.md#the-page-level-rule-for-async-environments).


# Is the thread pool safe under load?

Yes. Each top-level partial render takes one worker while it runs and queues when the pool is full. Nested partials render on their own thread, so nesting depth cannot exhaust the pool. The pool is created when the app starts serving and shut down when it stops, including after a failed startup. [How it works](how-it-works.md) has the tiers and the reasoning.


# What happens if I register twice?

On Flask and plain Jinja2, the second call simply replaces the global. On FastAPI and Starlette, each call wraps the lifespan again; on Quart, each call adds another pair of serving hooks. Register once, where the app is built.


# Is there a version for other template languages?

For Pyramid and Chameleon, see [chameleon_partials](https://github.com/mikeckennedy/chameleon_partials).


# Which Python versions are supported?

3.10 and newer. Older interpreters get 0.3.0 from pip; see [Installation](installation.md).

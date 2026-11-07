# Troubleshooting

Think of this page as a field guide. Each entry starts with what you actually see, on the page or in a traceback, because that is what you have in front of you when you arrive here. Then the cause, then the fix. Most of them are one line.


# The partial shows up as text, not HTML

What you see: the page displays `<div>` and friends literally, as if someone printed the template. View source shows `<div>`.

What happened: the environment has autoescaping on, [render_partial](../reference/render_partial.md#jinja_partials.render_partial) returned a plain `str` instead of `Markup`, and Jinja did its job and escaped it. The guilty party is almost always the plain Jinja2 path, because [register_environment](../reference/register_environment.md#jinja_partials.register_environment) defaults to `markup=False`. You can also get here by building your own renderer with `generate_render_partial(renderer, markup=False)`.

The fix: pass `markup=True` to [register_environment](../reference/register_environment.md#jinja_partials.register_environment) or [generate_render_partial](../reference/generate_render_partial.md#jinja_partials.generate_render_partial). The framework registrations and [PartialsJinjaExtension](../reference/PartialsJinjaExtension.md#jinja_partials.PartialsJinjaExtension) already do. Resist the urge to sprinkle `| safe` over every call site; that fixes the symptom fourteen times and the cause zero times.


# PartialsException: No renderer specified

What happened: [render_partial](../reference/render_partial.md#jinja_partials.render_partial) was called from Python with no `renderer` argument, and Flask is not installed, so there was no default renderer to fall back to. This is the library telling you it does not know how to render anything yet.

The fix: inside a web app, register with your framework and use the global from templates. From Python, pass `renderer=` explicitly, or bind one once with `generate_render_partial(renderer)` as shown in [custom renderers](how-it-works.md#one-primitive-and-some-sugar).


# PartialsException: Install Flask to use register_extensions

There are Quart, FastAPI, and Starlette editions of this message too. You called a registration function, and its framework could not be imported in this interpreter. Often this is a second virtual environment, a Docker image missing a dependency, or a test runner with a different Python than the one you ran the app with.

The fix: install the framework into the same environment as jinja_partials. The library never installs frameworks on your behalf; see [Installation](installation.md#bring-your-own-framework).


# AttributeError: 'Starlette' object has no attribute 'env'

What happened: [register_starlette_extensions](../reference/register_starlette_extensions.md#jinja_partials.register_starlette_extensions) was called with the app first, which is the FastAPI order. The function took your app, assumed it was a `Jinja2Templates`, and asked it for `.env`.

The fix: the Starlette signature is `register_starlette_extensions(templates, app=app)`. Templates first, app as a keyword. Yes, it is the reverse of FastAPI; [Frameworks](frameworks.md#starlette) explains why.


# jinja2.exceptions.TemplateNotFound: shared/partials/video_square.html

What happened: the name you passed does not resolve against the environment's loader. The error helpfully prints the name it looked for, so compare it character by character with the file on disk.

The fix: template names are paths relative to the templates root, forward slashes, extension included. Look for a stray leading slash, a missing subfolder, or a blueprint in Flask whose `template_folder` is not what you think it is.


# jinja2.exceptions.UndefinedError: 'video' is undefined

What happened: the partial reads a variable the caller never passed. This is not a bug in the library; it is the library's whole philosophy showing up in a traceback. Partials never see the caller's context. `{% include %}` would have silently handed over the page's `video`; [render_partial](../reference/render_partial.md#jinja_partials.render_partial) makes you say it out loud.

The fix: pass every value the fragment needs as a keyword argument, `render_partial('shared/partials/video_square.html', video=v)`. For optional inputs, let the fragment handle absence with `| default(...)`, the way the thumbnail partial handles `classes`.


# RuntimeError: asyncio.run() cannot be called from a running event loop

What happened: a FastAPI or Starlette route rendered the page with `templates.TemplateResponse(...)` or `template.render(...)` on an environment created with `enable_async=True`. Rendering an async template synchronously means calling `asyncio.run()` from inside the server's event loop, which Python refuses. Note the word page: the partials inside it were not involved.

The fix: render the page with `await template.render_async(...)` and return an `HTMLResponse`. The partials need no change; jinja_partials renders them on its own thread pool. [The page-level rule](frameworks.md#the-page-level-rule-for-async-environments) has the code.


# Context processor values are missing inside a partial

What happened: on Flask, you registered with [PartialsJinjaExtension](../reference/PartialsJinjaExtension.md#jinja_partials.PartialsJinjaExtension), and partials render through the Jinja environment, which does not run `@app.context_processor` functions. `g`, `request`, and `session` still work on that path, which can make the missing value feel random. It is not; only context processors and the `template_rendered` signal are skipped.

The fix: use `jinja_partials.register_extensions(app)`, the only registration that renders partials through `flask.render_template`.


# A request hangs while rendering nested partials

What happened: in versions up to 0.3.2, a nested partial in an async app waited on the same thread pool its outer partial was sitting in. Nest as deep as `max_workers`, or get enough concurrent requests with nested partials at once, and every worker was waiting for a worker. The pool never recovered.

The fix: upgrade. Nested renders now run on their own short-lived thread, so nesting depth never counts against `max_workers`. If you cannot upgrade yet, raise `max_workers` well above the deepest nesting multiplied by the concurrency you expect.


# The lifespan or startup hook runs twice

What happened: [register_fastapi_extensions](../reference/register_fastapi_extensions.md#jinja_partials.register_fastapi_extensions) or [register_starlette_extensions](../reference/register_starlette_extensions.md#jinja_partials.register_starlette_extensions) was called twice on one app. Each call wraps whatever lifespan is there, including the previous wrap; there is no idempotency guard. A second Quart registration likewise adds another pair of serving hooks. The usual culprit is an app factory that registers, plus a module that registers again at import.

The fix: register once, where the app is constructed, and make that the only caller.


# Nothing above matches

Open an issue at [github.com/mikeckennedy/jinja_partials/issues](https://github.com/mikeckennedy/jinja_partials/issues) with the registration call you used, the framework and its version, and the traceback. New entries in this field guide come from exactly those reports.

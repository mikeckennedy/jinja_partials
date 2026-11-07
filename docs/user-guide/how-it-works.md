# How it works

The whole library is one module. Understanding its three layers explains every behavior described elsewhere in this guide.


# One primitive and some sugar

`render_partial(template_name, renderer=None, markup=True, **data)` is the core. It calls `renderer(template_name, **data)` and, when `markup` is true, wraps the result in `markupsafe.Markup` so autoescaping leaves the fragment alone. With no renderer it falls back to `flask.render_template`, or raises [PartialsException](../reference/PartialsException.md#jinja_partials.PartialsException) when Flask is not installed.

`generate_render_partial(renderer, markup=True)` is `functools.partial` over [render_partial](../reference/render_partial.md#jinja_partials.render_partial) with the renderer bound. Every `register_*` function builds a framework-specific `renderer(template_name, **data) -> str` and installs the bound function as a Jinja global:

``` python
env.globals.update(render_partial=jinja_partials.generate_render_partial(renderer, markup=True))
```

That is also how you support a framework the library does not know about: write the renderer, bind it, install it.

``` python
def renderer(template_name: str, **data) -> str:
    return my_env.get_template(template_name).render(**data)

my_env.globals.update(render_partial=jinja_partials.generate_render_partial(renderer))
```

Because a partial renders through its own `renderer` call, it gets a fresh context containing only `data`. That is the mechanism behind the rule that partials see only what you pass them.


# Markup defaults

[render_partial](../reference/render_partial.md#jinja_partials.render_partial) and [generate_render_partial](../reference/generate_render_partial.md#jinja_partials.generate_render_partial) default to `markup=True`. The framework registrations and [PartialsJinjaExtension](../reference/PartialsJinjaExtension.md#jinja_partials.PartialsJinjaExtension) hardcode `markup=True`. [register_environment](../reference/register_environment.md#jinja_partials.register_environment) defaults to `markup=False` for backwards compatibility, which is why the plain Jinja2 path is the one place you have to say `markup=True` yourself. The type overloads encode this: `markup=True` returns `Markup` and `markup=False` returns `str`.


# Bridging async environments

Quart, FastAPI, and Starlette apps typically build their Jinja environment with `enable_async=True`. Templates in such an environment can only be rendered with `await template.render_async(...)`, but a Jinja expression like `{ render_partial(...) }` runs synchronously inside the page render and cannot await anything.

The renderer therefore submits `asyncio.run(template.render_async(**data))` to a `ThreadPoolExecutor` and blocks on the result. The worker thread has no running loop, so `asyncio.run` is legal there. The calling thread, which may be the server's event loop, waits for the fragment. This blocking is a deliberate tradeoff: partials are small and fast, and the alternative would require changing every template.

A nested partial is rendered from inside a worker thread that is itself blocked waiting for the outer render. Submitting the nested render back to the same pool could wait on a worker that never frees up, so nested renders run on a short-lived dedicated thread instead. `max_workers` only bounds how many top-level partial renders are in flight at once; nesting depth does not count against it.


# Three executor tiers

Which pool a render uses depends on how you registered and whether the app is serving.

1.  A dedicated pool, created when the app starts serving and shut down when it stops. FastAPI and Starlette get it by wrapping `app.router.lifespan_context`; the pool is stored on `app.state.jinja_partials_executor`. Quart gets it through `before_serving` and `after_serving` hooks; the pool is stored in `app.extensions['jinja_partials_executor']`.
2.  A lazy per-registration fallback pool, used for renders outside a serving cycle, for example in tests that never start the app. It honors the same `max_workers` and is never shut down.
3.  A module-level pool shared by [register_environment](../reference/register_environment.md#jinja_partials.register_environment), [PartialsJinjaExtension](../reference/PartialsJinjaExtension.md#jinja_partials.PartialsJinjaExtension), and [register_starlette_extensions](../reference/register_starlette_extensions.md#jinja_partials.register_starlette_extensions) without an app. It has four workers and is never shut down.

The lifecycle is exception-safe and re-entrant. The dedicated pool is created inside the lifespan wrapper and shut down in a `finally`, so a failed startup still cleans up and the app can start and stop repeatedly. The app state is cleared before the pool shuts down so concurrent renders fall back rather than submitting to a dying pool. Quart's startup hook replaces a stale pool left behind by a previously failed startup.


# Sizing max_workers

`max_workers` (default 4) on the Quart, FastAPI, and Starlette registrations sets the size of the dedicated and fallback pools. Each top-level partial render occupies one worker for the duration of that fragment. Renders beyond the pool size queue; they do not fail. Raise it if profiling shows requests waiting on partials under load. It has no effect on [register_starlette_extensions](../reference/register_starlette_extensions.md#jinja_partials.register_starlette_extensions) without an app or on the plain Jinja2 paths, which use the shared module-level pool.

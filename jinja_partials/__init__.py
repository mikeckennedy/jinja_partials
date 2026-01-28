"""
jinja_partials - Simple reuse of partial HTML page templates in the Jinja template language for Python web frameworks.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from functools import partial
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, Optional, Union

from jinja2 import Environment
from jinja2.ext import Extension
from jinja2.utils import concat
from markupsafe import Markup as Markup

try:
    __version__ = version('jinja_partials')
except PackageNotFoundError:
    __version__ = '0.0.0'
__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__all__ = [
    '__version__',
    'register_extensions',
    'register_quart_extensions',
    'register_fastapi_extensions',
    'register_starlette_extensions',
    'register_environment',
    'render_partial',
    'generate_render_partial',
    'PartialsException',
    'PartialsJinjaExtension',
]

# Thread pool for running async renders from sync context
_async_render_executor = ThreadPoolExecutor(max_workers=4)

try:
    import flask
except ImportError:
    flask = None

try:
    import quart
except ImportError:
    quart = None

try:
    import fastapi
except ImportError:
    fastapi = None

try:
    import starlette
except ImportError:
    starlette = None

if TYPE_CHECKING:
    if flask:
        from flask import Flask
    if quart:
        from quart import Quart
    if fastapi:
        from fastapi import FastAPI
        from fastapi.templating import Jinja2Templates as FastAPIJinja2Templates
    if starlette:
        from starlette.applications import Starlette
        from starlette.templating import Jinja2Templates


class PartialsException(Exception):
    pass


class PartialsJinjaExtension(Extension):
    """Jinja2 extension that automatically registers render_partial functionality.

    Usage:
        from jinja2 import Environment
        env = Environment(extensions=["jinja_partials.PartialsJinjaExtension"])

    The extension automatically makes render_partial available as a global
    function in templates. By default, markup is enabled.
    """

    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        # Use register_environment with markup=True to maintain same behavior
        register_environment(environment, markup=True)


def render_partial(
    template_name: str,
    renderer: Optional[Callable[..., Any]] = None,
    markup: bool = True,
    **data: Any,
) -> Union[Markup, str]:
    if renderer is None:
        if flask is None:
            raise PartialsException('No renderer specified')
        else:
            renderer = flask.render_template

    if markup:
        return Markup(renderer(template_name, **data))

    return renderer(template_name, **data)


def generate_render_partial(renderer: Callable[..., Any], markup: bool = True) -> Callable[..., Union[Markup, str]]:
    return partial(render_partial, renderer=renderer, markup=markup)


def register_extensions(app: 'Flask'):
    if flask is None:
        raise PartialsException('Install Flask to use `register_extensions`')

    app.jinja_env.globals.update(render_partial=generate_render_partial(flask.render_template))


def register_quart_extensions(app: 'Quart', max_workers: int = 4):
    """Register jinja_partials with a Quart application.

    This creates a dedicated ThreadPoolExecutor for rendering partials in async
    environments. The executor lifecycle is tied to the Quart app - it will be
    properly shut down when the app stops.

    Args:
        app: The Quart application instance.
        max_workers: Maximum number of worker threads for rendering partials.
                     Defaults to 4.
    """
    if quart is None:
        raise PartialsException('Install Quart to use `register_quart_extensions`')

    # Create a dedicated executor for this app
    executor = ThreadPoolExecutor(max_workers=max_workers)

    # Store executor on the app for potential access/debugging
    app.extensions['jinja_partials_executor'] = executor  # type: ignore[index]

    @app.after_serving
    async def shutdown_executor():
        executor.shutdown(wait=True)

    def renderer(template_name: str, **data: Any) -> str:
        env = app.jinja_env
        template = env.get_template(template_name)

        if env.is_async:
            # Run async render in the app's dedicated thread pool
            future = executor.submit(_run_async_render, template, data)
            return future.result()

        # Sync environment - use direct rendering (unlikely for Quart)
        ctx = template.new_context(data)
        try:
            return concat(template.root_render_func(ctx))
        except Exception:
            return env.handle_exception()

    app.jinja_env.globals.update(render_partial=generate_render_partial(renderer, markup=True))


def register_fastapi_extensions(
    app: 'FastAPI',
    templates: 'FastAPIJinja2Templates',
    max_workers: int = 4,
):
    """Register jinja_partials with a FastAPI application.

    This creates a dedicated ThreadPoolExecutor for rendering partials in async
    environments. The executor lifecycle is tied to the FastAPI app via its
    lifespan - it will be properly shut down when the app stops.

    Args:
        app: The FastAPI application instance.
        templates: The Jinja2Templates instance used for rendering.
        max_workers: Maximum number of worker threads for rendering partials.
                     Defaults to 4.

    Example:
        from fastapi import FastAPI
        from fastapi.templating import Jinja2Templates
        import jinja_partials

        app = FastAPI()
        templates = Jinja2Templates(directory="templates")
        jinja_partials.register_fastapi_extensions(app, templates)
    """
    if fastapi is None:
        raise PartialsException('Install FastAPI to use `register_fastapi_extensions`')

    # Create a dedicated executor for this app
    executor = ThreadPoolExecutor(max_workers=max_workers)

    # Store executor on app state for potential access/debugging
    app.state.jinja_partials_executor = executor

    # Wrap existing lifespan if present
    original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan_wrapper(app_instance: 'FastAPI') -> AsyncIterator[dict[str, Any]]:
        # Run original lifespan startup
        if original_lifespan is not None:
            async with original_lifespan(app_instance) as state:
                yield state if state else {} # type: ignore
        else:
            yield {}
        # Shutdown executor after app stops
        executor.shutdown(wait=True)

    app.router.lifespan_context = lifespan_wrapper

    env = templates.env

    def renderer(template_name: str, **data: Any) -> str:
        template = env.get_template(template_name)

        if env.is_async:
            # Run async render in the app's dedicated thread pool
            future = executor.submit(_run_async_render, template, data)
            return future.result()

        # Sync environment - use direct rendering
        ctx = template.new_context(data)
        try:
            return concat(template.root_render_func(ctx))
        except Exception:
            return env.handle_exception()

    env.globals.update(render_partial=generate_render_partial(renderer, markup=True))


def register_starlette_extensions(
    templates: 'Jinja2Templates',
    app: Optional['Starlette'] = None,
    max_workers: int = 4,
):
    """Register jinja_partials with Starlette templates.

    If an app is provided, creates a dedicated ThreadPoolExecutor with lifecycle
    management. Otherwise, uses the global executor (for backwards compatibility).

    Args:
        templates: The Jinja2Templates instance used for rendering.
        app: Optional Starlette application instance for lifecycle management.
        max_workers: Maximum number of worker threads for rendering partials.
                     Only used when app is provided. Defaults to 4.

    Example (with lifecycle management):
        from starlette.applications import Starlette
        from starlette.templating import Jinja2Templates
        import jinja_partials

        templates = Jinja2Templates(directory="templates")
        app = Starlette(...)
        jinja_partials.register_starlette_extensions(templates, app=app)

    Example (without lifecycle management - backwards compatible):
        jinja_partials.register_starlette_extensions(templates)
    """
    if starlette is None:
        raise PartialsException('Install Starlette to use `register_starlette_extensions`')

    env = templates.env

    if app is not None:
        # Create a dedicated executor for this app with lifecycle management
        executor = ThreadPoolExecutor(max_workers=max_workers)

        # Store executor on app state for potential access/debugging
        app.state.jinja_partials_executor = executor

        # Wrap existing lifespan if present
        original_lifespan = app.router.lifespan_context

        @asynccontextmanager
        async def lifespan_wrapper(app_instance: 'Starlette') -> AsyncIterator[dict[str, Any]]:
            # Run original lifespan startup
            if original_lifespan is not None:
                async with original_lifespan(app_instance) as state:
                    yield state if state else {} # type: ignore
            else:
                yield {}
            # Shutdown executor after app stops
            executor.shutdown(wait=True)

        app.router.lifespan_context = lifespan_wrapper

        def renderer(template_name: str, **data: Any) -> str:
            template = env.get_template(template_name)

            if env.is_async:
                future = executor.submit(_run_async_render, template, data)
                return future.result()

            ctx = template.new_context(data)
            try:
                return concat(template.root_render_func(ctx))
            except Exception:
                return env.handle_exception()

        env.globals.update(render_partial=generate_render_partial(renderer, markup=True))
    else:
        # Backwards compatible: use global executor
        def renderer(template_name: str, **data: Any) -> str:
            return _render_template_blocking(env, template_name, **data)  # type: ignore

        env.globals.update(render_partial=generate_render_partial(renderer))


def _run_async_render(template: Any, data: dict[str, Any]) -> str:
    """Run async template render in a new event loop (called from a thread)."""

    async def _do_render() -> str:
        return await template.render_async(**data)

    return asyncio.run(_do_render())


def _render_template_blocking(env: Environment, template_name: str, **data: Any) -> str:
    """Render a partial template, handling both sync and async Jinja environments.

    This function provides a synchronous interface for rendering partials, which is
    required because Jinja template expressions like {{ render_partial(...) }} cannot
    await async calls.

    For async environments (e.g., Quart with enable_async=True), we run the render
    in a separate thread with its own event loop to avoid the
    "cannot call asyncio.run() from running event loop" error.
    """
    template = env.get_template(template_name)

    # Check if templates are compiled for async (enable_async=True)
    if env.is_async:
        # Run async render in a separate thread with its own event loop
        future = _async_render_executor.submit(_run_async_render, template, data)
        return future.result()

    # Sync environment - use direct rendering
    ctx = template.new_context(data)
    try:
        return concat(template.root_render_func(ctx))
    except Exception:
        return env.handle_exception()


def register_environment(env: Environment, markup: bool = False):
    def renderer(template_name: str, **data: Any) -> str:
        return _render_template_blocking(env, template_name, **data)

    env.globals.update(render_partial=generate_render_partial(renderer, markup=markup))

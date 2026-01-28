"""
jinja_partials - Simple reuse of partial HTML page templates in the Jinja template language for Python web frameworks.
"""

__version__ = '0.3.0'
__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__all__ = [
    '__version__',
    'register_extensions',
    'register_starlette_extensions',
    'register_environment',
    'render_partial',
    'generate_render_partial',
    'PartialsException',
    'PartialsJinjaExtension',
]

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Optional, Union

from jinja2 import Environment
from jinja2.ext import Extension
from jinja2.utils import concat
from markupsafe import Markup as Markup

# Thread pool for running async renders from sync context
_async_render_executor = ThreadPoolExecutor(max_workers=4)

try:
    import flask
except ImportError:
    flask = None

try:
    import starlette
except ImportError:
    starlette = None

if TYPE_CHECKING and flask and starlette:
    from flask import Flask
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


def register_starlette_extensions(templates: 'Jinja2Templates'):
    if starlette is None:
        raise PartialsException('Install Starlette to use `register_starlette_extensions`')

    def renderer(template_name: str, **data: Any) -> str:
        return _render_template_blocking(templates.env, template_name, **data)  # type: ignore

    templates.env.globals.update(render_partial=generate_render_partial(renderer))  # type: ignore


def register_environment(env: Environment, markup: bool = False):
    def renderer(template_name: str, **data: Any) -> str:
        return _render_template_blocking(env, template_name, **data)

    env.globals.update(render_partial=generate_render_partial(renderer, markup=markup))

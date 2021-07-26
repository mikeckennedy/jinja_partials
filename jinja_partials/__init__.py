"""
jinja_partials - Simple reuse of partial HTML page templates in the Jinja template language for Python web frameworks.
"""

__version__ = '0.1.0'
__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__all__ = ['render_partial']

import flask as __flask
from jinja2 import Markup as Markup

has_registered_extensions = False


class PartialsException(Exception):
    pass


def render_partial(template_name: str, **data: dict) -> Markup:
    if not has_registered_extensions:
        raise PartialsException("You must call register_extensions() before this function can be used.")

    html = __flask.render_template(template_name, **data)
    return Markup(html)


def register_extensions(app: __flask.Flask):
    global has_registered_extensions

    has_registered_extensions = True
    app.jinja_env.globals.update(render_partial=render_partial)

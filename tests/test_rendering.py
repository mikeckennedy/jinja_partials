import sys
from types import SimpleNamespace
from typing import Callable, Union

# noinspection PyPackageRequirements
import pytest as pytest
from jinja2 import TemplateNotFound
from markupsafe import Markup

import jinja_partials


def test_render_empty(registered_extension):  # type: ignore
    html: Union[Markup, str] = jinja_partials.render_partial('render/bare.html')
    assert '<h1>This is bare HTML fragment</h1>' in html


def test_render_with_data(registered_extension):  # type: ignore
    name = 'Sarah'
    age = 32
    html: Union[Markup, str] = jinja_partials.render_partial('render/with_data.html', name=name, age=age)
    assert f'<span>Your name is {name} and age is {age}</span>' in html


def test_render_with_layout(registered_extension):  # type: ignore
    value_text = 'The message is clear'
    html: Union[Markup, str] = jinja_partials.render_partial('render/with_layout.html', message=value_text)
    assert '<title>Jinja Partials Test Template</title>' in html
    assert value_text in html


def test_render_recursive(registered_extension):  # type: ignore
    value_text = 'The message is clear'
    inner_text = 'The message is recursive'

    html: Union[Markup, str] = jinja_partials.render_partial(
        'render/recursive.html', message=value_text, inner=inner_text
    )
    assert value_text in html
    assert inner_text in html


def test_missing_template(registered_extension):  # type: ignore
    with pytest.raises(TemplateNotFound):
        jinja_partials.render_partial('no-way.pt', message=7)


def test_not_registered():
    with pytest.raises(Exception):
        jinja_partials.render_partial('doesnt-matter.pt', message=7)


def test_starlette_render_recursive(starlette_render_partial: Callable[..., Markup]):
    value_text = 'The message is clear'
    inner_text = 'The message is recursive'

    html = starlette_render_partial(
        'render/recursive.html',
        message=value_text,
        inner=inner_text,
    )
    assert value_text in html
    assert inner_text in html


def test_register_environment(environment_render_partial: Callable[..., Markup]):
    value_text = 'The message is clear'
    inner_text = 'The message is recursive'

    html = environment_render_partial(
        'render/recursive.html',
        message=value_text,
        inner=inner_text,
    )
    assert value_text in html
    assert inner_text in html


def test_register_extensions_raises_if_flask_is_not_installed():
    sys.modules['flask'] = None  # type: ignore
    del sys.modules['jinja_partials']
    import jinja_partials

    with pytest.raises(
        jinja_partials.PartialsException,
        match='Install Flask to use `register_extensions`',
    ):
        jinja_partials.register_extensions(SimpleNamespace())  # type: ignore
    del sys.modules['flask']


def test_register_extensions_raises_if_starlette_is_not_installed():
    sys.modules['starlette'] = None  # type: ignore
    del sys.modules['jinja_partials']
    import jinja_partials

    with pytest.raises(
        jinja_partials.PartialsException,
        match='Install Starlette to use `register_starlette_extensions`',
    ):
        jinja_partials.register_starlette_extensions(SimpleNamespace())  # type: ignore
    del sys.modules['starlette']

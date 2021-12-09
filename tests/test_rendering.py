from typing import Any, Callable

import jinja2
# noinspection PyPackageRequirements
import pytest as pytest
from jinja2 import TemplateNotFound

import jinja_partials
from fixtures import fastapi_render_partial, registered_extension


def test_render_empty(registered_extension):
    html: jinja2.Markup = jinja_partials.render_partial('render/bare.html')
    assert '<h1>This is bare HTML fragment</h1>' in html


def test_render_with_data(registered_extension):
    name = 'Sarah'
    age = 32
    html: jinja2.Markup = jinja_partials.render_partial('render/with_data.html', name=name, age=age)
    assert f'<span>Your name is {name} and age is {age}</span>' in html


def test_render_with_layout(registered_extension):
    value_text = "The message is clear"
    html: jinja2.Markup = jinja_partials.render_partial('render/with_layout.html', message=value_text)
    assert '<title>Jinja Partials Test Template</title>' in html
    assert value_text in html


def test_render_recursive(registered_extension):
    value_text = "The message is clear"
    inner_text = "The message is recursive"

    html: jinja2.Markup = jinja_partials.render_partial('render/recursive.html',
                                                        message=value_text,
                                                        inner=inner_text)
    assert value_text in html
    assert inner_text in html


def test_missing_template(registered_extension):
    with pytest.raises(TemplateNotFound):
        jinja_partials.render_partial('no-way.pt', message=7)


def test_not_registered():
    with pytest.raises(Exception):
        jinja_partials.render_partial('doesnt-matter.pt', message=7)


def test_fastapi_with_layout(fastapi_render_partial: Callable[..., Any]):
    value_text = "The message is clear"
    html: jinja2.Markup = fastapi_render_partial('render/with_layout.html', message=value_text)
    assert '<title>Jinja Partials Test Template</title>' in html
    assert value_text in html


def test_fastapi_recursive(fastapi_render_partial: Callable[..., Any]):
    value_text = "The message is clear"
    inner_text = "The message is recursive"

    html: jinja2.Markup = fastapi_render_partial('render/recursive.html',
                                                        message=value_text,
                                                        inner=inner_text)
    assert value_text in html
    assert inner_text in html

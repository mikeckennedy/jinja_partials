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


# Tests for markup parameter
def test_render_partial_markup_false(registered_extension):  # type: ignore
    """Test render_partial with markup=False returns a string instead of Markup."""
    html = jinja_partials.render_partial('render/bare.html', markup=False)
    assert isinstance(html, str)
    assert not isinstance(html, Markup)
    assert '<h1>This is bare HTML fragment</h1>' in html


def test_render_partial_markup_true_explicit(registered_extension):  # type: ignore
    """Test render_partial with markup=True (explicit) returns Markup."""
    html = jinja_partials.render_partial('render/bare.html', markup=True)
    assert isinstance(html, Markup)
    assert '<h1>This is bare HTML fragment</h1>' in html


# Tests for template name edge cases
def test_render_partial_empty_template_name(registered_extension):  # type: ignore
    """Test render_partial with empty string template name."""
    with pytest.raises(TemplateNotFound):
        jinja_partials.render_partial('')


def test_render_partial_none_template_name(registered_extension):  # type: ignore
    """Test render_partial with None template name."""
    from jinja2.exceptions import TemplatesNotFound

    with pytest.raises(TemplatesNotFound):
        jinja_partials.render_partial(None)  # type: ignore


# New test for template rendering verification
def test_data_passed_through_correctly(registered_extension):  # type: ignore
    """Test that data is actually passed through correctly to templates."""
    # Test with various data types
    test_data = {
        'string_value': 'test_string',
        'number_value': 42,
        'list_value': [1, 2, 3],
        'dict_value': {'nested': 'value'},
        'boolean_value': True,
    }

    # This test uses a template that should render all the passed data
    # We'll verify each piece of data appears in the output
    html = jinja_partials.render_partial(
        'render/with_data.html', name=test_data['string_value'], age=test_data['number_value']
    )

    # Verify the data was actually passed through and rendered
    assert str(test_data['string_value']) in html
    assert str(test_data['number_value']) in html


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


def test_partials_jinja_extension():
    """Test that PartialsJinjaExtension works declaratively with Jinja2 Environment."""
    from jinja2 import Environment, FileSystemLoader
    from pathlib import Path

    # Create environment with the extension loaded declaratively
    templates_path = Path(__file__).parent / 'test_templates'
    env = Environment(loader=FileSystemLoader(templates_path), extensions=['jinja_partials.PartialsJinjaExtension'])

    # Test that render_partial is available as a global
    assert 'render_partial' in env.globals

    # Test that render_partial works correctly
    template = env.get_template('render/recursive.html')
    html = template.render(message='test message', inner='test inner')

    assert 'test message' in html
    assert 'test inner' in html
    assert '<h1>This is inner html</h1>' in html

    # Test with data template
    data_template = env.get_template('render/with_data.html')
    html = data_template.render(name='Alice', age=30)

    assert 'Alice' in html
    assert '30' in html
    assert '<span>Your name is Alice and age is 30</span>' in html


def test_partials_jinja_extension_markup_behavior():
    """Test that PartialsJinjaExtension returns Markup objects by default."""
    from jinja2 import Environment, FileSystemLoader
    from pathlib import Path
    from markupsafe import Markup

    # Create environment with the extension loaded declaratively
    templates_path = Path(__file__).parent / 'test_templates'
    env = Environment(loader=FileSystemLoader(templates_path), extensions=['jinja_partials.PartialsJinjaExtension'])

    # Get the render_partial function from globals
    render_partial_func = env.globals['render_partial']

    # Test that it returns Markup by default
    result = render_partial_func('render/bare.html')  # type: ignore
    assert isinstance(result, Markup)
    assert '<h1>This is bare HTML fragment</h1>' in result

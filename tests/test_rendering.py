import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import AbstractAsyncContextManager
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, Callable, Union, cast

# noinspection PyPackageRequirements
import pytest as pytest
from jinja2 import Environment, TemplateNotFound
from markupsafe import Markup

import jinja_partials

if TYPE_CHECKING:
    from quart import Quart

_TEMPLATES_DIR = Path(__file__).parent / 'test_templates'


def _render_partial_global(env: Environment) -> Callable[..., str]:
    """Fetch the installed ``render_partial`` global with a callable type.

    jinja2 leaves ``Environment.globals`` unannotated, so type checkers infer its value type from the
    default globals and refuse to call anything read out of it.
    """
    return cast('Callable[..., str]', env.globals['render_partial'])


def _serving(app: 'Quart') -> AbstractAsyncContextManager[Any]:
    """``async with`` wrapper for ``app.test_app()``.

    Quart's ``TestAppProtocol`` declares ``__aexit__`` with non-Optional exception parameters, which
    type checkers reject as an async context manager.
    """
    return cast('AbstractAsyncContextManager[Any]', app.test_app())


def test_render_empty(registered_extension):
    html: Union[Markup, str] = jinja_partials.render_partial('render/bare.html')
    assert '<h1>This is bare HTML fragment</h1>' in html


def test_render_with_data(registered_extension):
    name = 'Sarah'
    age = 32
    html: Union[Markup, str] = jinja_partials.render_partial('render/with_data.html', name=name, age=age)
    assert f'<span>Your name is {name} and age is {age}</span>' in html


def test_render_with_layout(registered_extension):
    value_text = 'The message is clear'
    html: Union[Markup, str] = jinja_partials.render_partial('render/with_layout.html', message=value_text)
    assert '<title>Jinja Partials Test Template</title>' in html
    assert value_text in html


def test_render_recursive(registered_extension):
    value_text = 'The message is clear'
    inner_text = 'The message is recursive'

    html: Union[Markup, str] = jinja_partials.render_partial(
        'render/recursive.html', message=value_text, inner=inner_text
    )
    assert value_text in html
    assert inner_text in html


def test_missing_template(registered_extension):
    with pytest.raises(TemplateNotFound):
        jinja_partials.render_partial('no-way.pt', message=7)


def test_not_registered():
    with pytest.raises(Exception):
        jinja_partials.render_partial('doesnt-matter.pt', message=7)


# Tests for markup parameter
def test_render_partial_markup_false(registered_extension):
    """Test render_partial with markup=False returns a string instead of Markup."""
    html = jinja_partials.render_partial('render/bare.html', markup=False)
    assert isinstance(html, str)
    assert not isinstance(html, Markup)
    assert '<h1>This is bare HTML fragment</h1>' in html


def test_render_partial_markup_true_explicit(registered_extension):
    """Test render_partial with markup=True (explicit) returns Markup."""
    html = jinja_partials.render_partial('render/bare.html', markup=True)
    assert isinstance(html, Markup)
    assert '<h1>This is bare HTML fragment</h1>' in html


# Tests for template name edge cases
def test_render_partial_empty_template_name(registered_extension):
    """Test render_partial with empty string template name."""
    with pytest.raises(TemplateNotFound):
        jinja_partials.render_partial('')


def test_render_partial_none_template_name(registered_extension):
    """Test render_partial with None template name."""
    from jinja2.exceptions import TemplatesNotFound

    with pytest.raises(TemplatesNotFound):
        jinja_partials.render_partial(None)  # type: ignore


# New test for template rendering verification
def test_data_passed_through_correctly(registered_extension):
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
    from pathlib import Path

    from jinja2 import Environment, FileSystemLoader

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


# Tests for executor lifecycle management (re-entrant startup/shutdown cycles)
def _track_executors(monkeypatch):
    """Patch jinja_partials.ThreadPoolExecutor to record every pool created and its submissions."""
    created = []

    class RecordingExecutor(ThreadPoolExecutor):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.submitted = 0
            self.requested_max_workers = kwargs.get('max_workers')
            created.append(self)

        def submit(self, *args, **kwargs):
            self.submitted += 1
            return super().submit(*args, **kwargs)

    monkeypatch.setattr(jinja_partials, 'ThreadPoolExecutor', RecordingExecutor)
    return created


def _async_templates():
    from pathlib import Path

    from fastapi.templating import Jinja2Templates
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(Path(__file__).parent / 'test_templates'), enable_async=True)
    return Jinja2Templates(env=env)


def test_fastapi_executor_lifecycle_reentrant(monkeypatch):
    """Each lifespan cycle gets a fresh executor and renders go through it."""
    import asyncio
    from pathlib import Path

    from fastapi import FastAPI
    from fastapi.templating import Jinja2Templates
    from jinja2 import Environment, FileSystemLoader

    created = _track_executors(monkeypatch)
    env = Environment(loader=FileSystemLoader(Path(__file__).parent / 'test_templates'), enable_async=True)
    templates = Jinja2Templates(env=env)
    app = FastAPI()
    jinja_partials.register_fastapi_extensions(app, templates)
    fallback = created[0]
    render = _render_partial_global(templates.env)

    async def cycle():
        async with app.router.lifespan_context(app):
            executor = app.state.jinja_partials_executor
            assert executor is not None
            html = render('render/bare.html')
            assert '<h1>This is bare HTML fragment</h1>' in html
            assert executor.submitted == 1  # the render used the per-cycle executor
            return executor

    first = asyncio.run(cycle())
    second = asyncio.run(cycle())

    assert first is not second
    for executor in (first, second):
        with pytest.raises(RuntimeError):
            executor.submit(print)

    # Outside a lifespan cycle, rendering uses the per-registration fallback
    assert app.state.jinja_partials_executor is None
    assert fallback.submitted == 0
    html = render('render/bare.html')
    assert '<h1>This is bare HTML fragment</h1>' in html
    assert fallback.submitted == 1


def test_fastapi_executor_shutdown_on_lifespan_error():
    """The executor is shut down even when the wrapped lifespan raises."""
    import asyncio
    from contextlib import asynccontextmanager
    from pathlib import Path

    from fastapi import FastAPI
    from fastapi.templating import Jinja2Templates
    from jinja2 import Environment, FileSystemLoader

    @asynccontextmanager
    async def failing_lifespan(app):
        yield {}
        raise RuntimeError('boom in shutdown')

    env = Environment(loader=FileSystemLoader(Path(__file__).parent / 'test_templates'), enable_async=True)
    templates = Jinja2Templates(env=env)
    app = FastAPI(lifespan=failing_lifespan)
    jinja_partials.register_fastapi_extensions(app, templates)

    captured = {}

    async def cycle():
        async with app.router.lifespan_context(app):
            captured['executor'] = app.state.jinja_partials_executor

    with pytest.raises(RuntimeError, match='boom in shutdown'):
        asyncio.run(cycle())

    assert app.state.jinja_partials_executor is None
    with pytest.raises(RuntimeError):
        captured['executor'].submit(print)


def test_fastapi_executor_shutdown_on_startup_error(monkeypatch):
    """The executor is shut down even when the wrapped lifespan raises during startup."""
    import asyncio
    from contextlib import asynccontextmanager
    from pathlib import Path

    from fastapi import FastAPI
    from fastapi.templating import Jinja2Templates
    from jinja2 import Environment, FileSystemLoader

    created = _track_executors(monkeypatch)

    @asynccontextmanager
    async def failing_lifespan(app):
        raise RuntimeError('boom in startup')
        yield {}  # unreachable, makes this an async generator

    env = Environment(loader=FileSystemLoader(Path(__file__).parent / 'test_templates'), enable_async=True)
    templates = Jinja2Templates(env=env)
    app = FastAPI(lifespan=failing_lifespan)
    jinja_partials.register_fastapi_extensions(app, templates)
    render = _render_partial_global(templates.env)

    async def cycle():
        async with app.router.lifespan_context(app):
            pass  # never reached, startup fails

    with pytest.raises(RuntimeError, match='boom in startup'):
        asyncio.run(cycle())

    # The per-cycle executor (created after the registration fallback) was shut down
    assert app.state.jinja_partials_executor is None
    with pytest.raises(RuntimeError):
        created[1].submit(print)

    # Rendering still works via the per-registration fallback
    html = render('render/bare.html')
    assert '<h1>This is bare HTML fragment</h1>' in html


def test_starlette_executor_lifecycle_reentrant(monkeypatch):
    """Each lifespan cycle gets a fresh executor and renders go through it."""
    import asyncio
    from pathlib import Path

    from jinja2 import Environment, FileSystemLoader
    from starlette.applications import Starlette
    from starlette.templating import Jinja2Templates

    created = _track_executors(monkeypatch)
    env = Environment(loader=FileSystemLoader(Path(__file__).parent / 'test_templates'), enable_async=True)
    templates = Jinja2Templates(env=env)
    app = Starlette()
    jinja_partials.register_starlette_extensions(templates, app=app)
    fallback = created[0]
    render = _render_partial_global(templates.env)

    async def cycle():
        async with app.router.lifespan_context(app):
            executor = app.state.jinja_partials_executor
            assert executor is not None
            html = render('render/bare.html')
            assert '<h1>This is bare HTML fragment</h1>' in html
            assert executor.submitted == 1  # the render used the per-cycle executor
            return executor

    first = asyncio.run(cycle())
    second = asyncio.run(cycle())

    assert first is not second

    # Outside a lifespan cycle, rendering uses the per-registration fallback
    assert app.state.jinja_partials_executor is None
    assert fallback.submitted == 0
    html = render('render/bare.html')
    assert '<h1>This is bare HTML fragment</h1>' in html
    assert fallback.submitted == 1


def test_starlette_executor_shutdown_on_lifespan_error():
    """The executor is shut down even when the wrapped lifespan raises."""
    import asyncio
    from contextlib import asynccontextmanager
    from pathlib import Path

    from jinja2 import Environment, FileSystemLoader
    from starlette.applications import Starlette
    from starlette.templating import Jinja2Templates

    @asynccontextmanager
    async def failing_lifespan(app):
        yield
        raise RuntimeError('boom in shutdown')

    env = Environment(loader=FileSystemLoader(Path(__file__).parent / 'test_templates'), enable_async=True)
    templates = Jinja2Templates(env=env)
    app = Starlette(lifespan=failing_lifespan)
    jinja_partials.register_starlette_extensions(templates, app=app)

    captured = {}

    async def cycle():
        async with app.router.lifespan_context(app):
            captured['executor'] = app.state.jinja_partials_executor

    with pytest.raises(RuntimeError, match='boom in shutdown'):
        asyncio.run(cycle())

    assert app.state.jinja_partials_executor is None
    with pytest.raises(RuntimeError):
        captured['executor'].submit(print)


def test_quart_executor_lifecycle_reentrant(monkeypatch):
    """Each serving cycle gets a fresh executor and renders go through it."""
    import asyncio
    from pathlib import Path

    from quart import Quart

    created = _track_executors(monkeypatch)
    folder = (Path(__file__).parent / 'test_templates').as_posix()
    app = Quart(__name__, template_folder=folder)
    jinja_partials.register_quart_extensions(app)
    fallback = created[0]
    render = _render_partial_global(app.jinja_env)

    async def cycle():
        async with _serving(app):
            executor = app.extensions['jinja_partials_executor']
            assert executor is not None
            html = render('render/bare.html')
            assert '<h1>This is bare HTML fragment</h1>' in html
            assert executor.submitted == 1  # the render used the per-cycle executor
            return executor

    first = asyncio.run(cycle())
    second = asyncio.run(cycle())

    assert first is not second

    # Outside a serving cycle, rendering uses the per-registration fallback
    assert app.extensions['jinja_partials_executor'] is None
    assert fallback.submitted == 0
    html = render('render/bare.html')
    assert '<h1>This is bare HTML fragment</h1>' in html
    assert fallback.submitted == 1


def test_starlette_executor_shutdown_on_startup_error(monkeypatch):
    """The executor is shut down even when the wrapped lifespan raises during startup."""
    import asyncio
    from contextlib import asynccontextmanager

    from starlette.applications import Starlette

    created = _track_executors(monkeypatch)

    @asynccontextmanager
    async def failing_lifespan(app):
        raise RuntimeError('boom in startup')
        yield  # unreachable, makes this an async generator

    templates = _async_templates()
    app = Starlette(lifespan=failing_lifespan)
    jinja_partials.register_starlette_extensions(templates, app=app)
    render = _render_partial_global(templates.env)

    async def cycle():
        async with app.router.lifespan_context(app):
            pass  # never reached, startup fails

    with pytest.raises(RuntimeError, match='boom in startup'):
        asyncio.run(cycle())

    # The per-cycle executor (created after the registration fallback) was shut down
    assert app.state.jinja_partials_executor is None
    with pytest.raises(RuntimeError):
        created[1].submit(print)

    # Rendering still works via the per-registration fallback
    html = render('render/bare.html')
    assert '<h1>This is bare HTML fragment</h1>' in html


def test_fastapi_lifespan_state_passthrough():
    """Wrapping preserves the user lifespan: both phases run and state passes through."""
    import asyncio
    from contextlib import asynccontextmanager

    from fastapi import FastAPI

    ran = {'startup': False, 'shutdown': False}

    @asynccontextmanager
    async def user_lifespan(app):
        ran['startup'] = True
        yield {'answer': 42}
        ran['shutdown'] = True

    templates = _async_templates()
    app = FastAPI(lifespan=user_lifespan)
    jinja_partials.register_fastapi_extensions(app, templates)

    async def cycle():
        async with app.router.lifespan_context(app) as state:
            assert ran['startup']
            assert state == {'answer': 42}

    asyncio.run(cycle())
    assert ran['shutdown']


def test_fastapi_render_before_first_startup(monkeypatch):
    """Partials render via the per-registration fallback before any lifespan cycle."""
    from fastapi import FastAPI

    created = _track_executors(monkeypatch)
    templates = _async_templates()
    app = FastAPI()
    jinja_partials.register_fastapi_extensions(app, templates)

    html = _render_partial_global(templates.env)('render/bare.html')
    assert '<h1>This is bare HTML fragment</h1>' in html
    assert created[0].submitted == 1  # the registration fallback did the work


def test_fastapi_nested_partials_in_cycle():
    """Nested partials render through the executor without deadlocking."""
    import asyncio

    from fastapi import FastAPI

    templates = _async_templates()
    app = FastAPI()
    jinja_partials.register_fastapi_extensions(app, templates)
    render = _render_partial_global(templates.env)

    async def cycle():
        async with app.router.lifespan_context(app):
            html = render('render/recursive.html', message='outer message', inner='inner message')
            assert 'outer message' in html
            assert 'inner message' in html
            assert '<h1>This is inner html</h1>' in html

    asyncio.run(cycle())


def test_executor_max_workers_passthrough(monkeypatch):
    """The requested max_workers reaches both the per-cycle and fallback executors."""
    import asyncio
    from pathlib import Path

    from fastapi import FastAPI
    from quart import Quart
    from starlette.applications import Starlette

    created = _track_executors(monkeypatch)

    fastapi_app = FastAPI()
    jinja_partials.register_fastapi_extensions(fastapi_app, _async_templates(), max_workers=7)

    starlette_app = Starlette()
    jinja_partials.register_starlette_extensions(_async_templates(), app=starlette_app, max_workers=7)

    quart_app = Quart(__name__, template_folder=(Path(__file__).parent / 'test_templates').as_posix())
    jinja_partials.register_quart_extensions(quart_app, max_workers=7)

    async def cycles():
        async with fastapi_app.router.lifespan_context(fastapi_app):
            pass
        async with starlette_app.router.lifespan_context(starlette_app):
            pass
        async with _serving(quart_app):
            pass

    asyncio.run(cycles())

    # 3 registration fallbacks + 3 per-cycle executors, all with the requested size
    assert len(created) == 6
    assert all(executor.requested_max_workers == 7 for executor in created)


def test_quart_executor_recovers_from_failed_startup():
    """A failed startup leaves a stale executor; the next start replaces and shuts it down."""
    import asyncio
    from pathlib import Path

    from quart import Quart

    folder = (Path(__file__).parent / 'test_templates').as_posix()
    app = Quart(__name__, template_folder=folder)
    jinja_partials.register_quart_extensions(app)

    fail = {'on': True}

    @app.before_serving
    async def maybe_fail():
        if fail['on']:
            raise RuntimeError('boom in startup')

    async def failed_cycle():
        async with _serving(app):
            pass  # never reached, startup fails

    with pytest.raises(Exception, match='boom in startup'):
        asyncio.run(failed_cycle())

    # after_serving never ran, so the slot still holds the orphaned executor
    stale = app.extensions['jinja_partials_executor']
    assert stale is not None

    fail['on'] = False

    async def clean_cycle():
        async with _serving(app):
            fresh = app.extensions['jinja_partials_executor']
            assert fresh is not None
            assert fresh is not stale
            html = _render_partial_global(app.jinja_env)('render/bare.html')
            assert '<h1>This is bare HTML fragment</h1>' in html

    asyncio.run(clean_cycle())

    # The self-healing startup shut the stale executor down
    with pytest.raises(RuntimeError):
        stale.submit(print)
    assert app.extensions['jinja_partials_executor'] is None


def test_partials_jinja_extension_markup_behavior():
    """Test that PartialsJinjaExtension returns Markup objects by default."""
    from pathlib import Path

    from jinja2 import Environment, FileSystemLoader
    from markupsafe import Markup

    # Create environment with the extension loaded declaratively
    templates_path = Path(__file__).parent / 'test_templates'
    env = Environment(loader=FileSystemLoader(templates_path), extensions=['jinja_partials.PartialsJinjaExtension'])

    # Get the render_partial function from globals
    render_partial_func = _render_partial_global(env)

    # Test that it returns Markup by default
    result = render_partial_func('render/bare.html')
    assert isinstance(result, Markup)
    assert '<h1>This is bare HTML fragment</h1>' in result


# Tests for nested partials vs. executor capacity (a nested render must not wait on the pool it occupies)
def test_nested_partials_deeper_than_max_workers(monkeypatch):
    """A nested partial renders on its own thread, so nesting depth never exhausts the pool."""
    import asyncio
    import threading

    from fastapi import FastAPI

    created = _track_executors(monkeypatch)
    templates = _async_templates()
    app = FastAPI()
    jinja_partials.register_fastapi_extensions(app, templates, max_workers=1)
    render = _render_partial_global(templates.env)
    outcome = {}

    def run():
        async def cycle():
            async with app.router.lifespan_context(app):
                outcome['html'] = render('render/recursive.html', message='outer message', inner='inner message')

        asyncio.run(cycle())

    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    worker.join(timeout=10)
    assert not worker.is_alive(), 'nested render deadlocked the single-worker pool'
    assert 'outer message' in outcome['html']
    assert 'inner message' in outcome['html']
    # Only the outer render went through the per-cycle pool; the nested one ran on a dedicated thread
    assert created[1].submitted == 1


def test_concurrent_nested_partials_do_not_exhaust_pool():
    """Outer partials that fill every worker can still render their nested partials."""
    import asyncio
    import threading

    from fastapi import FastAPI

    templates = _async_templates()
    app = FastAPI()
    jinja_partials.register_fastapi_extensions(app, templates, max_workers=2)
    render = _render_partial_global(templates.env)
    # Both outer renders occupy the pool before either one nests
    barrier = threading.Barrier(2, timeout=10)
    results = []

    def request():
        results.append(render('render/nested_barrier.html', sync=barrier.wait, inner='inner message'))

    def run():
        async def cycle():
            async with app.router.lifespan_context(app):
                threads = [threading.Thread(target=request, daemon=True) for _ in range(2)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join(timeout=10)

        asyncio.run(cycle())

    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    worker.join(timeout=20)
    assert not worker.is_alive(), 'nested renders deadlocked the pool'
    assert len(results) == 2
    assert all('<span>The inner text is inner message</span>' in html for html in results)


# Tests for template names that leave the templates folder. Jinja's loader refuses them; these pin the
# contract that every built-in renderer hands the name to that loader untouched.
_ESCAPING_NAMES = [
    '../conftest.py',
    ' ../conftest.py',
    '\t../conftest.py',
    '\n../conftest.py',
    'render/ ../../conftest.py',
    'render\\..\\..\\conftest.py',
    '/etc/hosts',
    str(_TEMPLATES_DIR.parent / 'conftest.py'),  # absolute path to a real file
    'render',
    'render/',
    ' render/bare.html',
]
_REGISTRATION_PATHS = ['flask', 'jinja', 'jinja_async', 'fastapi', 'starlette', 'quart']


@pytest.fixture
def every_render_partial(registered_extension):
    """The installed render_partial global of each registration path, none inside a serving cycle."""
    from fastapi import FastAPI
    from fastapi.templating import Jinja2Templates
    from jinja2 import Environment, FileSystemLoader
    from quart import Quart

    sync_env = Environment(loader=FileSystemLoader(_TEMPLATES_DIR))
    jinja_partials.register_environment(sync_env)
    async_env = Environment(loader=FileSystemLoader(_TEMPLATES_DIR), enable_async=True)
    jinja_partials.register_environment(async_env)
    fastapi_templates = Jinja2Templates(directory=_TEMPLATES_DIR)
    jinja_partials.register_fastapi_extensions(FastAPI(), fastapi_templates)
    starlette_templates = Jinja2Templates(directory=_TEMPLATES_DIR)
    jinja_partials.register_starlette_extensions(starlette_templates)
    quart_app = Quart(__name__, template_folder=str(_TEMPLATES_DIR))
    jinja_partials.register_quart_extensions(quart_app)

    return {
        'flask': jinja_partials.render_partial,
        'jinja': _render_partial_global(sync_env),
        'jinja_async': _render_partial_global(async_env),
        'fastapi': _render_partial_global(fastapi_templates.env),
        'starlette': _render_partial_global(starlette_templates.env),
        'quart': _render_partial_global(quart_app.jinja_env),
    }


@pytest.mark.parametrize('path', _REGISTRATION_PATHS)
def test_names_inside_the_folder_render_on_every_path(every_render_partial, path):
    assert '<h1>This is bare HTML fragment</h1>' in every_render_partial[path]('render/bare.html')


@pytest.mark.parametrize('name', _ESCAPING_NAMES, ids=repr)
@pytest.mark.parametrize('path', _REGISTRATION_PATHS)
def test_names_outside_the_folder_are_not_found(every_render_partial, path, name):
    with pytest.raises(TemplateNotFound):
        every_render_partial[path](name)


# Tests for runaway nesting: a partial that renders itself must end in RecursionError, not a crash or a stall.
# In an async environment every nested level is its own thread and event loop, so the library caps the depth.
def _nested_render_threads():
    import threading

    return [t for t in threading.enumerate() if t.name == 'jinja_partials-nested-render']


def _plain_render_partial(is_async: bool):
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(_TEMPLATES_DIR), enable_async=is_async)
    jinja_partials.register_environment(env)
    return _render_partial_global(env)


@pytest.mark.parametrize('is_async', [False, True], ids=['sync', 'async'])
def test_partial_rendering_itself_raises_recursion_error(is_async):
    render = _plain_render_partial(is_async)
    with pytest.raises(RecursionError):
        render('render/self_cycle.html', n=0)
    assert not _nested_render_threads(), 'nested render threads were left behind'
    # The per-thread depth is restored on the way out, so later renders still work
    assert '<h1>This is bare HTML fragment</h1>' in render('render/bare.html')


def test_async_nesting_depth_is_capped(monkeypatch):
    """The cap is MAX_NESTED_RENDERS levels, the first on the pool and each further level on one thread."""
    import threading

    started = []
    original_start = threading.Thread.start

    def counting_start(self):
        started.append(self.name)
        original_start(self)

    monkeypatch.setattr(threading.Thread, 'start', counting_start)
    render = _plain_render_partial(is_async=True)
    with pytest.raises(RecursionError, match='render/self_cycle.html'):
        render('render/self_cycle.html', n=0)
    nested = [name for name in started if name == 'jinja_partials-nested-render']
    assert len(nested) == jinja_partials.MAX_NESTED_RENDERS - 1


@pytest.mark.parametrize('is_async', [False, True], ids=['sync', 'async'])
def test_deeply_nested_partials_still_render(is_async):
    render = _plain_render_partial(is_async)
    assert '<span>bottom 20</span>' in render('render/deep.html', n=0, limit=20)
    assert not _nested_render_threads()

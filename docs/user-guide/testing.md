# Testing partials

Partials are plain template files with explicit inputs, which makes them easy to test on their own, without a browser or a full page. The patterns below are the ones the library's own test suite uses.


# Flask

[render_partial](../reference/render_partial.md#jinja_partials.render_partial) with no renderer falls back to `flask.render_template`, which needs an app and request context. A fixture provides both:

``` python
import flask
import pytest
import jinja_partials


@pytest.fixture
def app():
    app = flask.Flask(__name__, template_folder='templates')
    jinja_partials.register_extensions(app)
    with app.test_request_context('/'):
        yield app


def test_video_square(app):
    html = jinja_partials.render_partial('shared/partials/video_square.html', video=FakeVideo())
    assert '12,500 views' in html
```

A missing template raises `jinja2.TemplateNotFound`, so `pytest.raises(TemplateNotFound)` is the right assertion for a bad name.


# FastAPI and Starlette

After registration, the bound function is the [render_partial](../reference/render_partial.md#jinja_partials.render_partial) global on the environment. Call it directly, with or without a running lifespan:

``` python
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
import jinja_partials

templates = Jinja2Templates(directory='templates')
app = FastAPI()
jinja_partials.register_fastapi_extensions(app, templates)


def test_card_partial():
    render = templates.env.globals['render_partial']
    html = render('shared/partials/card.html', item={'title': 'Python Basics'})
    assert 'Python Basics' in html
```

Outside a lifespan, async environments render through a per-registration fallback pool, so this works in a plain test function. For full request tests, `with TestClient(app) as client:` runs the lifespan; the pool is created on entry and shut down on exit, and the app can be started and stopped as many times as the suite needs.


# Quart

Quart's `app.test_app()` context runs the `before_serving` and `after_serving` hooks, which is where the render pool lives. Drive it with `asyncio.run` from a synchronous test:

``` python
import asyncio
from quart import Quart
import jinja_partials


def test_quart_partial():
    app = Quart(__name__, template_folder='templates')
    jinja_partials.register_quart_extensions(app)

    async def cycle():
        async with app.test_app():
            return app.jinja_env.globals['render_partial']('shared/partials/badge.html', tag='beginner')

    assert 'beginner' in asyncio.run(cycle())
```


# Plain Jinja2

``` python
from jinja2 import Environment, FileSystemLoader
import jinja_partials

env = Environment(loader=FileSystemLoader('templates'), autoescape=True)
jinja_partials.register_environment(env, markup=True)


def test_fragment():
    html = env.get_template('home/index.html').render(videos=[FakeVideo()])
    assert '<img src=' in html
```

Assert on `isinstance(result, Markup)` if your test is specifically about escaping behavior; [render_partial](../reference/render_partial.md#jinja_partials.render_partial) returns `markupsafe.Markup` whenever `markup=True`.

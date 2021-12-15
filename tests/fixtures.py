from pathlib import Path
from functools import partial
from typing import Any

import flask
# noinspection PyPackageRequirements
import pytest

import jinja_partials

from fastapi.templating import Jinja2Templates

@pytest.fixture
def registered_extension():
    folder = (Path(__file__).parent / "test_templates").as_posix()
    app = flask.Flask(__name__, template_folder=folder)

    @app.get('/hello')
    def hello():
        ...

    with app.test_request_context('/hello', method='POST'):
        jinja_partials.register_extensions(app)

        # Allow test to work with extensions as registered
        yield

        # Roll back the fact that we registered the extensions for future tests.
        jinja_partials.has_registered_extensions = False



@pytest.fixture
def starlette_render_partial():
    templates = Jinja2Templates(Path(__file__).parent / "test_templates")
    jinja_partials.register_starlette_extensions(templates)

    def renderer(template_name: str, **data: Any) -> str:
        return templates.get_template(template_name).render(**data)

    return partial(jinja_partials.render_partial, renderer=renderer)
    
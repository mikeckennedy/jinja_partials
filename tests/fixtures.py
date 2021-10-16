from pathlib import Path

import flask
# noinspection PyPackageRequirements
import pytest

import jinja_partials


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

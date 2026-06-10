import flask
from views import home

import jinja_partials

app = flask.Flask(__name__)

# Option 1: Traditional registration (active)
jinja_partials.register_extensions(app)

# Option 2: Or use the extension with Flask's jinja environment (commented out)
# app.jinja_env.add_extension('jinja_partials.PartialsJinjaExtension')


app.register_blueprint(home.blueprint)

if __name__ == '__main__':
    print(f'Running demo app with jinja-partials=={jinja_partials.__version__}.')
    app.run(debug=True, port=5001)

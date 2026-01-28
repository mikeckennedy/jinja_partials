import flask

import jinja_partials
from views import home

app = flask.Flask(__name__)

# Option 1: Or use the traditional registration (commented out)
jinja_partials.register_extensions(app)

# Option 2: Use the extension with Flask's jinja environment
# app.jinja_env.add_extension('jinja_partials.PartialsJinjaExtension')


app.register_blueprint(home.blueprint)

if __name__ == '__main__':
    print(f'Running demo app with jinja-partials=={jinja_partials.__version__}.')
    app.run(debug=True, port=5001)

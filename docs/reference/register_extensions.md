## register_extensions()


Register jinja_partials with a Flask application.


Usage

``` python
register_extensions(app)
```


Makes render_partial available as a global function in the app's Jinja templates, rendering with flask.render_template.


## Parameters


`app: Flask`  
The Flask application instance.


## Raises


`PartialsException`  
If Flask is not installed.


## Example

Register once at startup:

``` python
import flask
import jinja_partials

app = flask.Flask(__name__)
jinja_partials.register_extensions(app)
```

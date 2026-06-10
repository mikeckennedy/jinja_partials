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

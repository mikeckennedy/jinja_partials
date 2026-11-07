## PartialsException


Raised when jinja_partials is misconfigured or a required web framework is not installed.


Usage

``` python
PartialsException()
```


Every `register_*` function raises it when its framework cannot be imported, and [render_partial](render_partial.md#jinja_partials.render_partial) raises it when called with no renderer outside Flask. A template that cannot be found raises `jinja2.TemplateNotFound` instead.


## Example

Catch it to give a clearer startup error:

``` python
import jinja_partials

try:
    jinja_partials.register_quart_extensions(app)
except jinja_partials.PartialsException as e:
    raise SystemExit(f'jinja_partials setup failed: {e}')
```

## PartialsJinjaExtension


Jinja2 extension that automatically registers render_partial functionality.


Usage

``` python
PartialsJinjaExtension(environment)
```


The extension automatically makes render_partial available as a global function in templates. By default, markup is enabled.


## Note

Partials registered this way render directly through the Jinja2 environment rather than flask.render_template, so Flask context processors do not apply inside partials. Flask apps that rely on context processors should use register_extensions instead.


## Parameters


`environment: Environment`  
The Jinja2 environment the extension is loaded into. Jinja2 passes this automatically when the class is listed in extensions=\[…\].


## Example

Enable the extension on a Jinja2 environment:

    from jinja2 import Environment
    env = Environment(extensions=["jinja_partials.PartialsJinjaExtension"])

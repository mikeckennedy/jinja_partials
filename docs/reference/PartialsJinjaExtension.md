## PartialsJinjaExtension


Jinja2 extension that automatically registers render_partial functionality.


Usage

``` python
PartialsJinjaExtension()
```


The extension automatically makes render_partial available as a global function in templates. By default, markup is enabled.


## Example

Enable the extension on a Jinja2 environment:

    from jinja2 import Environment
    env = Environment(extensions=["jinja_partials.PartialsJinjaExtension"])

## generate_render_partial()


Create a render_partial function bound to a specific renderer.


Usage

``` python
generate_render_partial(renderer: Callable[..., Any], markup: Literal[True] = ...) -> Callable[..., Markup]
 
generate_render_partial(renderer: Callable[..., Any], markup: Literal[False]) -> Callable[..., str]
 
generate_render_partial(renderer: Callable[..., Any], markup: bool) -> Callable[..., Union[Markup, str]]
```


## Parameters


`renderer: Callable[..., Any]`  
Callable that renders a template name plus keyword arguments to a string.

`markup: bool = True`  
When True (the default), results are wrapped in markupsafe.Markup.


## Returns


`Callable[..., Union[Markup, str]]`  
A callable with the same signature as render_partial that uses the bound renderer.


## Example

Install a custom renderer as the [render_partial](render_partial.md#jinja_partials.render_partial) global:

``` python
def renderer(template_name: str, **data) -> str:
    return env.get_template(template_name).render(**data)


env.globals.update(render_partial=jinja_partials.generate_render_partial(renderer))
```

## generate_render_partial()


Create a render_partial function bound to a specific renderer.


Usage

``` python
generate_render_partial(
    renderer,
    markup=True,
)
```


## Parameters


`renderer: Callable[…, Any]`  
Callable that renders a template name plus keyword arguments to a string.

`markup: bool = ``True`  
When True (the default), results are wrapped in markupsafe.Markup.


## Returns


`Callable[…, Union[Markup, str]]`  
A callable with the same signature as render_partial that uses the bound renderer.

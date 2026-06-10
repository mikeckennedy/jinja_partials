## render_partial()


Render a partial template and return the resulting HTML fragment.


Usage

``` python
render_partial(template_name: str, renderer: Optional[Callable[..., Any]] = ..., markup: Literal[True] = ..., data: Any = {}) -> Markup
 
render_partial(template_name: str, renderer: Optional[Callable[..., Any]] = ..., markup: Literal[False], data: Any = {}) -> str
 
render_partial(template_name: str, renderer: Optional[Callable[..., Any]] = ..., markup: bool = ..., data: Any = {}) -> Union[Markup, str]
```


## Parameters


`template_name: str`  
Path of the template within the templates folder, e.g. `shared/partials/video_image.html`.

`renderer: Optional[Callable[..., Any]] = None`  
Callable that renders the template with the given keyword arguments. Defaults to flask.render_template when Flask is installed.

`markup: bool = ``True`  
When True (the default), wrap the result in markupsafe.Markup so it is not re-escaped when inserted into another template.

`**data: Any`  
Model data passed to the template as keyword arguments.


## Returns


`Union[Markup, str]`  
The rendered fragment as Markup, or str when markup=False.


## Raises


`PartialsException`  
If no renderer is specified and Flask is not installed.

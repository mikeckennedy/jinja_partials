## render_partial()


Render a partial template and return the resulting HTML fragment.


Usage

``` python
render_partial(template_name: str, renderer: Optional[Callable[..., Any]] = ..., markup: Literal[True] = ..., **data: Any) -> Markup
 
render_partial(template_name: str, renderer: Optional[Callable[..., Any]] = ..., markup: Literal[False], **data: Any) -> str
 
render_partial(template_name: str, renderer: Optional[Callable[..., Any]] = ..., markup: bool = ..., **data: Any) -> Union[Markup, str]
```


## Parameters


`template_name: str`  
Path of the template within the templates folder, e.g. `shared/partials/video_image.html`. Names that leave the folder raise `jinja2.TemplateNotFound`; map any request-supplied value to a name you wrote rather than building the path from it.

`renderer: Optional[Callable[..., Any]] = None`  
Callable that renders the template with the given keyword arguments. Defaults to flask.render_template when Flask is installed.

`markup: bool = True`  
When True (the default), wrap the result in markupsafe.Markup so it is not re-escaped when inserted into another template.

`**data: Any`  
Model data passed to the template as keyword arguments.


## Returns


`Union[Markup, str]`  
The rendered fragment as Markup, or str when markup=False.


## Raises


`PartialsException`  
If no renderer is specified and Flask is not installed.


## Example

Inside a template, after any `register_*` call:

``` html
{{ render_partial('shared/partials/video_square.html', video=v) }}
```

From Python in a Flask request context, for example in a test:

``` python
html = jinja_partials.render_partial('shared/partials/video_square.html', video=video)
```

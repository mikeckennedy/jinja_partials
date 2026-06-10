## register_starlette_extensions()


Register jinja_partials with Starlette templates.


Usage

``` python
register_starlette_extensions(
    templates,
    app=None,
    max_workers=4,
)
```


If an app is provided, creates a dedicated ThreadPoolExecutor with lifecycle management. Otherwise, uses the global executor (for backwards compatibility).


## Parameters


`templates: Jinja2Templates`  
The Jinja2Templates instance used for rendering.

`app: Optional[Starlette] = None`  
Optional Starlette application instance for lifecycle management.

`max_workers: int = ``4`  
Maximum number of worker threads for rendering partials. Only used when app is provided. Defaults to 4.


## Raises


`PartialsException`  
If Starlette is not installed.


## Example

With lifecycle management:

    from starlette.applications import Starlette
    from starlette.templating import Jinja2Templates
    import jinja_partials

    templates = Jinja2Templates(directory="templates")
    app = Starlette(...)
    jinja_partials.register_starlette_extensions(templates, app=app)

Without lifecycle management (backwards compatible):

    jinja_partials.register_starlette_extensions(templates)

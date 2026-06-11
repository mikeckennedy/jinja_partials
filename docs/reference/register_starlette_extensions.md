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


If an app is provided, creates a dedicated ThreadPoolExecutor when the app's lifespan starts and shuts it down when the lifespan exits - even if startup or shutdown raises - so the app can be started and stopped repeatedly; outside lifespan cycles, async renders use a per-registration fallback executor with the same max_workers. Without an app, partials render directly for sync environments, or via a shared module-level executor for async (enable_async=True) environments.


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

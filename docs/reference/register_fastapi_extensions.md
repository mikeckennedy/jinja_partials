## register_fastapi_extensions()


Register jinja_partials with a FastAPI application.


Usage

``` python
register_fastapi_extensions(
    app,
    templates,
    max_workers=4,
)
```


This creates a dedicated ThreadPoolExecutor for rendering partials in async environments. The executor lifecycle is tied to the FastAPI app via its lifespan - it is shut down when the lifespan exits normally (one startup/shutdown cycle per registration).


## Parameters


`app: FastAPI`  
The FastAPI application instance.

`templates: FastAPIJinja2Templates`  
The Jinja2Templates instance used for rendering.

`max_workers: int = ``4`  
Maximum number of worker threads for rendering partials. Defaults to 4.


## Raises


`PartialsException`  
If FastAPI is not installed.


## Example

Register during app setup:

    from fastapi import FastAPI
    from fastapi.templating import Jinja2Templates
    import jinja_partials

    app = FastAPI()
    templates = Jinja2Templates(directory="templates")
    jinja_partials.register_fastapi_extensions(app, templates)

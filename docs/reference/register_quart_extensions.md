## register_quart_extensions()


Register jinja_partials with a Quart application.


Usage

``` python
register_quart_extensions(
    app,
    max_workers=4,
)
```


This creates a dedicated ThreadPoolExecutor for rendering partials in async environments. The executor lifecycle is tied to the Quart app - it will be properly shut down when the app stops.


## Parameters


`app: Quart`  
The Quart application instance.

`max_workers: int = ``4`  
Maximum number of worker threads for rendering partials. Defaults to 4.


## Raises


`PartialsException`  
If Quart is not installed.

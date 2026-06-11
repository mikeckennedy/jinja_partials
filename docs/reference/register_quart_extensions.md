## register_quart_extensions()


Register jinja_partials with a Quart application.


Usage

``` python
register_quart_extensions(
    app,
    max_workers=4,
)
```


This creates a dedicated ThreadPoolExecutor for rendering partials in async environments. The executor is created when the app starts serving and shut down when it stops, so the app can be started and stopped repeatedly (an executor left behind by a failed startup is replaced on the next start). Outside a serving cycle, partials render via a per-registration fallback executor with the same max_workers.


## Parameters


`app: Quart`  
The Quart application instance.

`max_workers: int = ``4`  
Maximum number of worker threads for rendering partials. Defaults to 4.


## Raises


`PartialsException`  
If Quart is not installed.

## register_environment()


Register jinja_partials with a plain Jinja2 environment.


Usage

``` python
register_environment(
    env,
    markup=False,
)
```


Use this for standalone Jinja2 usage or frameworks without dedicated support. Handles both sync and async (enable_async=True) environments.


## Parameters


`env: Environment`  
The Jinja2 Environment to make render_partial available in.

`markup: bool = ``False`  
When True, wrap rendered partials in markupsafe.Markup. Defaults to False.

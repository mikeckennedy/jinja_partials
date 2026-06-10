# API Reference


Public API for jinja_partials: framework registration, partial rendering, and the Jinja2 extension.


## Framework registration


Register render_partial with your web framework once at app startup.


[register_extensions()](register_extensions.md#jinja_partials.register_extensions)  
Register jinja_partials with a Flask application.

[register_fastapi_extensions()](register_fastapi_extensions.md#jinja_partials.register_fastapi_extensions)  
Register jinja_partials with a FastAPI application.

[register_starlette_extensions()](register_starlette_extensions.md#jinja_partials.register_starlette_extensions)  
Register jinja_partials with Starlette templates.

[register_quart_extensions()](register_quart_extensions.md#jinja_partials.register_quart_extensions)  
Register jinja_partials with a Quart application.

[register_environment()](register_environment.md#jinja_partials.register_environment)  
Register jinja_partials with a plain Jinja2 environment.


## Rendering


Render partial templates directly or build framework-specific renderers.


[render_partial()](render_partial.md#jinja_partials.render_partial)  
Render a partial template and return the resulting HTML fragment.

[generate_render_partial()](generate_render_partial.md#jinja_partials.generate_render_partial)  
Create a render_partial function bound to a specific renderer.


## Jinja2 extension


Declarative registration via the Jinja2 extension mechanism.


[PartialsJinjaExtension](PartialsJinjaExtension.md#jinja_partials.PartialsJinjaExtension)  
Jinja2 extension that automatically registers render_partial functionality.


## Exceptions


Errors raised by jinja_partials.


[PartialsException](PartialsException.md#jinja_partials.PartialsException)  
Raised when jinja_partials is misconfigured or a required web framework is not installed.

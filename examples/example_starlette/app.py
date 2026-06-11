from pathlib import Path

import jinja2
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates

import jinja_partials

# enable_async=True is the case the executor machinery exists for; partials
# inside these templates render on the executor managed by register_starlette_extensions.
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(Path(__file__).parent / 'templates'),
    autoescape=True,
    enable_async=True,
)
templates = Jinja2Templates(env=env)


async def index(request):
    items = [
        {
            'title': 'Python Basics',
            'author': 'Alice',
            'views': 12500,
            'tag': 'beginner',
        },
        {'title': 'Async Patterns', 'author': 'Bob', 'views': 8750, 'tag': 'advanced'},
        {
            'title': 'Web Development',
            'author': 'Carol',
            'views': 23100,
            'tag': 'intermediate',
        },
    ]
    # An async environment renders pages via render_async; TemplateResponse would
    # call asyncio.run() inside the running event loop and fail.
    template = templates.get_template('home/index.html')
    return HTMLResponse(await template.render_async(items=items))


app = Starlette(debug=True, routes=[Route('/', index)])

# Register jinja_partials with Starlette (ties executor lifecycle to app)
jinja_partials.register_starlette_extensions(templates, app=app)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=10002)

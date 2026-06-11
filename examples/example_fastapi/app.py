from pathlib import Path

import jinja2
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import jinja_partials

app = FastAPI()

# enable_async=True is the case the executor machinery exists for; partials
# inside these templates render on the executor managed by register_fastapi_extensions.
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(Path(__file__).parent / 'templates'),
    autoescape=True,
    enable_async=True,
)
templates = Jinja2Templates(env=env)

# Register jinja_partials with FastAPI (ties executor lifecycle to app)
jinja_partials.register_fastapi_extensions(app, templates)


@app.get('/')
async def index() -> HTMLResponse:
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


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=10003)

from pathlib import Path

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.templating import Jinja2Templates

import jinja_partials

templates = Jinja2Templates(directory=Path(__file__).parent / 'templates')


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
    return templates.TemplateResponse(request, 'home/index.html', {'items': items})


app = Starlette(debug=True, routes=[Route('/', index)])

# Register jinja_partials with Starlette (ties executor lifecycle to app)
jinja_partials.register_starlette_extensions(templates, app=app)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=10002)

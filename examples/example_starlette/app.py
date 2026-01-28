import jinja_partials
from pathlib import Path
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.templating import Jinja2Templates
from starlette.responses import HTMLResponse

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Register jinja_partials with Starlette's Jinja environment
jinja_partials.register_environment(templates.env, markup=True)


async def index(request):
    items = [
        {
            "title": "Python Basics",
            "author": "Alice",
            "views": 12500,
            "tag": "beginner",
        },
        {"title": "Async Patterns", "author": "Bob", "views": 8750, "tag": "advanced"},
        {
            "title": "Web Development",
            "author": "Carol",
            "views": 23100,
            "tag": "intermediate",
        },
    ]
    return templates.TemplateResponse(request, "home/index.html", {"items": items})


app = Starlette(debug=True, routes=[Route("/", index)])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=10002)

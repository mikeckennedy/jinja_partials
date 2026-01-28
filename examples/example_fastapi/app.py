import jinja_partials
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Register jinja_partials with FastAPI's Jinja environment
jinja_partials.register_environment(templates.env, markup=True)


@app.get("/")
async def index(request: Request):
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=10003)

from quart import Quart, render_template

import jinja_partials

app = Quart(__name__)

# Register jinja_partials with the Quart app (manages its own render executor)
jinja_partials.register_quart_extensions(app)


@app.get('/')
async def index():
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
    return await render_template('home/index.html', items=items)


if __name__ == '__main__':
    app.run(debug=True, port=10001)

#!/usr/bin/env python3

"""
Example demonstrating the use of jinja_partials.PartialsJinjaExtension

This shows how to use the jinja_partials extension declaratively
by adding it to the Jinja2 Environment extensions list.
"""

from jinja2 import Environment, DictLoader

# Create a simple template loader with some example templates
templates = {
    'main.html': """
<html>
<head><title>{{ title }}</title></head>
<body>
    <h1>{{ title }}</h1>
    <div class="content">
        {{ render_partial('content.html', message=message) }}
    </div>
    <footer>
        {{ render_partial('footer.html', year=year) }}
    </footer>
</body>
</html>
    """.strip(),
    'content.html': """
<div class="message">
    <p>{{ message }}</p>
    <p>This content was rendered as a partial!</p>
</div>
    """.strip(),
    'footer.html': """
<div class="footer">
    <p>&copy; {{ year }} - Powered by jinja_partials</p>
</div>
    """.strip(),
}


def main():
    print('=== jinja_partials Extension Example ===\n')

    # -- DECLARATIVE-USE: Just declare that you want to use it.
    environment = Environment(loader=DictLoader(templates), extensions=['jinja_partials.PartialsJinjaExtension'])

    # Render the main template
    template = environment.get_template('main.html')
    html = template.render(
        title='Welcome to jinja_partials!', message='Hello from the partial template system!', year=2024
    )

    print('Rendered HTML:')
    print('=' * 50)
    print(html)
    print('=' * 50)
    print()

    # Verify that render_partial is available as a global
    print('Available globals in environment:')
    for name in sorted(environment.globals.keys()):
        if not name.startswith('_'):  # Skip private globals
            print(f'  - {name}')

    print(f'\nrender_partial is available: {"render_partial" in environment.globals}')


if __name__ == '__main__':
    main()

# Quickstart

Remember the fourteen video cards from [Why partials](why-partials.md)? This page builds one, properly, with Flask, and then serves that same card to HTMX for free. Every other framework differs only in the registration line, and [Frameworks](frameworks.md) has those. Four files and a few minutes.


# 1. Register once at startup

``` python
# app.py
import flask
import jinja_partials

app = flask.Flask(__name__)
jinja_partials.register_extensions(app)


@app.get('/')
def index():
    return flask.render_template('home/index.html', videos=get_videos())
```

That one line installs [render_partial](../reference/render_partial.md#jinja_partials.render_partial) as a global in the app's Jinja environment. Do it where the app is built, before it starts serving, and do it once. There is no need to import anything in your templates; the function is simply there, like `url_for`.


# 2. Give the partials a home

Partials are ordinary templates, so they can live anywhere your loader can see. The convention this project uses, and the one the examples follow, is a `partials` folder under `templates/shared`:

``` text
templates/
├── home/
│   └── index.html
└── shared/
    ├── _layout.html
    └── partials/
        ├── video_image.html
        └── video_square.html
```

When you call [render_partial](../reference/render_partial.md#jinja_partials.render_partial), the name you pass is the path relative to the templates root, forward slashes and file extension included, exactly as you would write it for `render_template`. Nothing clever, which is the point.


# 3. Write the partials, smallest first

The innermost fragment is the YouTube thumbnail. It takes a `video` and an optional list of CSS classes:

``` html
<!-- templates/shared/partials/video_image.html -->
<img src="https://img.youtube.com/vi/{{ video.id }}/maxresdefault.jpg"
     class="img img-responsive {{ (classes | default([])) | join(' ') }}"
     alt="{{ video.title }}"
     title="{{ video.title }}">
```

Notice `classes | default([])`. The fragment declares that `classes` is optional by handling its absence itself. Callers that do not care never have to know it exists.

Now the card. It wraps the thumbnail in a link, adds the author and the view count, and it does so by rendering the image partial inside itself. Partials nest; that is half their charm.

``` html
<!-- templates/shared/partials/video_square.html -->

    [{{ render_partial('shared/partials/video_image.html', video=video) }}](https://www.youtube.com/watch?v={{ video.id }})
    [{{ video.author }}](https://www.youtube.com/watch?v={{ video.id }})
    <div class="views">{{ "{:,}".format(video.views) }} views</div>

```


# 4. Call it from a page

``` html
<!-- templates/home/index.html -->
{% extends "shared/_layout.html" %}
{% block main_content %}
    {% for v in videos %}
        <div class="col-md-3 video">
            {{ render_partial('shared/partials/video_square.html', video=v) }}
        </div>
    {% endfor %}
{% endblock %}
```

The page calls the loop variable `v`. The card calls it `video`. That renaming at the boundary is not a workaround; it is how partials are meant to be used. The fragment names what it needs, and each caller maps its own data onto those names. The listing page, the search results, and the email digest can all call this one file with whatever they happen to have.


# 5. What you should see

Run the app and open the page. Each video renders as a card like this, with the thumbnail inlined where the nested [render_partial](../reference/render_partial.md#jinja_partials.render_partial) call used to be:

``` html

    <div>
        <a href="https://www.youtube.com/watch?v=abc123" target="_blank">
            <img src="https://img.youtube.com/vi/abc123/maxresdefault.jpg" class="img img-responsive " alt="Intro to Flask" title="Intro to Flask">
        </a>
        [Talk Python](https://www.youtube.com/watch?v=abc123)
        <div class="views">12,500 views</div>
    </div>

```

If instead the page shows you the HTML itself as text, angle brackets and all, the fragment was inserted as an escaped string rather than as markup. On Flask that does not happen, but on the plain Jinja2 path it is the single most common surprise, and [Troubleshooting](troubleshooting.md) has the one-word fix along with every other error you are likely to meet.


# 6. Hand the same card to HTMX

Here is the payoff for building the card as a file rather than a macro. The view counts on the home page go stale the moment the page loads, and the product manager would like them to tick along without a refresh. With HTMX, each card asks the server for a fresh copy of itself every thirty seconds:

``` html
<!-- templates/home/index.html -->
{% for v in videos %}
    <div class="col-md-3 video" hx-get="/videos/{{ v.id }}/card" hx-trigger="every 30s" hx-swap="innerHTML">
        {{ render_partial('shared/partials/video_square.html', video=v) }}
    </div>
{% endfor %}
```

The route that answers those requests does not need [render_partial](../reference/render_partial.md#jinja_partials.render_partial) at all. A partial is an ordinary template, so the framework's normal render call serves it straight to the browser:

``` python
@app.get('/videos/<video_id>/card')
def video_card(video_id):
    return flask.render_template('shared/partials/video_square.html', video=get_video(video_id))
```

One file, two delivery routes. The page inlines the card with [render_partial](../reference/render_partial.md#jinja_partials.render_partial) on the first visit, HTMX fetches the very same file from the route after that, and the markup is identical both ways because it came from the same template with the same `video`. A macro could not do this; there is no URL for a macro.

On FastAPI and Starlette the route is `HTMLResponse(await templates.get_template('shared/partials/video_square.html').render_async(video=video))`, and on Quart it is `await render_template(...)`, which is to say the same page-level rule from [Frameworks](frameworks.md#the-page-level-rule-for-async-environments) applies to a fragment response too.

The complete version of this app, with the layout, the CSS, and a small JSON database of videos, is the [Flask example](https://github.com/mikeckennedy/jinja_partials/tree/main/examples/example_flask) in the repository. It is the app behind the screenshot on the README.

# Flask demo app

This is the app behind the screenshot on the project README: a small video site where every card on the page comes from one partial file. It is the long version of the [Quickstart](https://mkennedy.codes/docs/jinja-partials/user-guide/quickstart.html), with the layout, the CSS, and a JSON database the guide leaves out.

## Run it

```bash
pip install -r examples/example_flask/requirements.txt
python examples/example_flask/app.py
```

Then open <http://127.0.0.1:5001>. The app runs in debug mode, so template edits show up on refresh.

## Where to look

- `app.py` registers jinja_partials with the one line that matters, `jinja_partials.register_extensions(app)`. The commented-out alternative is the declarative `PartialsJinjaExtension` route. It works too, with one trade-off the [Frameworks](https://mkennedy.codes/docs/jinja-partials/user-guide/frameworks.html#the-declarative-extension) page explains: Flask context processors do not run inside partials on that path.
- `templates/shared/partials/video_image.html` is the innermost fragment, a YouTube thumbnail that takes a `video` and an optional list of CSS `classes`.
- `templates/shared/partials/video_square.html` is the card. It renders the thumbnail partial inside itself, which is the nesting the guide keeps mentioning.
- `templates/home/index.html` and `templates/home/listing.html` are two pages that render the same card in a loop. Change the card once and both pages change.
- `views/home.py` is a blueprint with the two routes, and `services/video_service.py` reads `db/videos.json`. Nothing in the Python layer knows that partials exist.

## Without the server

`example_use_jinja_partials.py` is a standalone script. It builds a Jinja2 environment from a dictionary of templates, enables `PartialsJinjaExtension` declaratively, and prints the rendered HTML:

```bash
python examples/example_flask/example_use_jinja_partials.py
```

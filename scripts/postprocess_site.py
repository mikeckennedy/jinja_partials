#!/usr/bin/env python3
"""Post-process the mirrored docs/ site to fix Great Docs 0.13 output bugs.

Run by build_docs.py after mirroring great-docs/_site -> docs/. Each fix is
narrow and idempotent; counts are printed so a silent no-op is visible when a
future Great Docs release changes its output (at which point these may be
removable).

Fixes:
1. Insert <link rel="canonical"> on every page (Great Docs emits og:url and the
   sitemap from seo.canonical.base_url but never the canonical tag itself).
2. search.json points 5 entries at skill.html; the built page is skills.html.
3. reference/*.html load video-embed.js without the ../ prefix (404).
4. The inline color-swatch.js loader strips two path segments from the page
   URL, which only works for pages one level deep; on root-level pages it
   resolves outside the subpath (404). Rewritten to strip one segment there
   (correct with the canonical tag from fix 1, including the / homepage URL).
5. Homepage og:url lacks the trailing slash the sitemap uses.
6. Homepage <title>/og:title/twitter:title duplicate the site name
   ("Jinja Partials | Jinja Partials").
"""

from __future__ import annotations

import sys
from pathlib import Path

BASE_URL = 'https://mkennedy.codes/docs/jinja-partials/'
DOCS = Path(__file__).resolve().parent.parent / 'docs'

HOME_TITLE = 'Jinja Partials – Partial HTML templates for Python web frameworks'
DOUBLE_STRIP = ".href.replace(/\\/[^\\/]*$/,'').replace(/\\/[^\\/]*$/,'')+'/color-swatch.js'"
SINGLE_STRIP = ".href.replace(/\\/[^\\/]*$/,'')+'/color-swatch.js'"


def canonical_url(rel: Path) -> str:
    posix = rel.as_posix()
    if posix == 'index.html':
        return BASE_URL
    if posix.endswith('/index.html'):
        return BASE_URL + posix[: -len('index.html')]
    return BASE_URL + posix


def main() -> int:
    if not DOCS.is_dir():
        print(f'docs/ missing: {DOCS}', file=sys.stderr)
        return 1

    counts = {'canonical': 0, 'video_embed': 0, 'color_swatch': 0}

    for page in sorted(DOCS.rglob('*.html')):
        rel = page.relative_to(DOCS)
        text = page.read_text(encoding='utf-8')
        original = text

        if '<link rel="canonical"' not in text and '</head>' in text:
            tag = f'<link rel="canonical" href="{canonical_url(rel)}">\n'
            text = text.replace('</head>', tag + '</head>', 1)
            counts['canonical'] += 1

        if rel.parent.as_posix() == 'reference' and '<script src="video-embed.js">' in text:
            text = text.replace('<script src="video-embed.js">', '<script src="../video-embed.js">')
            counts['video_embed'] += 1

        if rel.parent == Path('.') and DOUBLE_STRIP in text:
            text = text.replace(DOUBLE_STRIP, SINGLE_STRIP)
            counts['color_swatch'] += 1

        if rel.as_posix() == 'index.html':
            text = text.replace(
                'content="https://mkennedy.codes/docs/jinja-partials"',
                f'content="{BASE_URL}"',
            )
            text = text.replace('<title>Jinja Partials | Jinja Partials</title>', f'<title>{HOME_TITLE}</title>')
            text = text.replace('content="Jinja Partials | Jinja Partials"', f'content="{HOME_TITLE}"')

        if text != original:
            page.write_text(text, encoding='utf-8')

    search = DOCS / 'search.json'
    skill_fixes = 0
    if search.is_file():
        text = search.read_text(encoding='utf-8')
        skill_fixes = text.count('skill.html')
        if skill_fixes:
            search.write_text(text.replace('skill.html', 'skills.html'), encoding='utf-8')

    print(
        f'[postprocess_site] canonical tags: {counts["canonical"]}, '
        f'video-embed paths: {counts["video_embed"]}, '
        f'color-swatch loaders: {counts["color_swatch"]}, '
        f'search.json skill->skills: {skill_fixes}'
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

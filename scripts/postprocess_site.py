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
7. Pandoc smart typography leaks into code spans: type annotations render with
   a Unicode ellipsis (Callable[…, Any]) and literals with curly quotes, so
   copied text is invalid Python. Restore ASCII inside <code> spans (HTML) and
   backtick spans (reference/*.md).
8. The class Usage signature drops __init__ parameters, rendering the
   misleading no-arg constructor 'PartialsJinjaExtension()'.
9. The render_partial Usage signatures render the **data var-keyword as a
   positional 'data: Any = {}' parameter (HTML and .md companion).
10. In the reference/*.md parameter lists a default value is wrapped in its
    own backticks inside the code span ('`markup: bool = ``True`'), which
    Markdown renders as a broken span. Collapsed to '`markup: bool = True`'.
11. The navbar version badge comes from the latest GitHub Release, so docs
    built before that release is published show the previous version. The
    badge is rewritten to the pyproject.toml version, dated from that version's
    change-log.md heading, so docs can be built before the release exists.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = 'https://mkennedy.codes/docs/jinja-partials/'
DOCS = ROOT / 'docs'
_VERSION_BADGE = re.compile(r'<span class="version-badge"[^>]*>[^<]*</span>')

HOME_TITLE = 'Jinja Partials – Partial HTML templates for Python web frameworks'
DOUBLE_STRIP = ".href.replace(/\\/[^\\/]*$/,'').replace(/\\/[^\\/]*$/,'')+'/color-swatch.js'"
SINGLE_STRIP = ".href.replace(/\\/[^\\/]*$/,'')+'/color-swatch.js'"

_CODE_SPAN = re.compile(r'(<code[^>]*>)(.*?)(</code>)', re.DOTALL)
_MD_CODE_SPAN = re.compile(r'`[^`\n]+`')
_SMART_CHARS = {'…': '...', '‘': "'", '’': "'", '“': '"', '”': '"'}

EXT_SIG_HTML = '<span class="sig-name">PartialsJinjaExtension</span>()'
EXT_SIG_HTML_FIXED = '<span class="sig-name">PartialsJinjaExtension</span>(environment)'
EXT_SIG_MD = 'PartialsJinjaExtension()'
EXT_SIG_MD_FIXED = 'PartialsJinjaExtension(environment)'

DATA_SIG_HTML = '<span class="va">data</span>: <span class="va">Any</span> <span class="op">=</span> {})'
DATA_SIG_HTML_FIXED = '<span class="op">**</span><span class="va">data</span>: <span class="va">Any</span>)'
DATA_SIG_MD = 'data: Any = {})'
DATA_SIG_MD_FIXED = '**data: Any)'
_MD_NESTED_DEFAULT = re.compile(r'`([^`\n]+ = )``([^`\n]+)`')


def _unsmart(text: str) -> str:
    for bad, good in _SMART_CHARS.items():
        text = text.replace(bad, good)
    return text


def fix_code_spans(text: str, pattern: re.Pattern[str]) -> tuple[str, int]:
    fixed = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal fixed
        whole = m.group(0)
        clean = _unsmart(whole)
        if clean != whole:
            fixed += 1
        return clean

    return pattern.sub(repl, text), fixed


def version_badge() -> str:
    """Badge HTML for the pyproject.toml version, dated from its change-log.md heading."""
    version = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
    changelog = (ROOT / 'change-log.md').read_text(encoding='utf-8')
    m = re.search(rf'^## \[{re.escape(version)}\] - (\d{{4}}-\d{{2}}-\d{{2}})', changelog, re.MULTILINE)
    if not m:
        print(f'[postprocess_site] WARNING: no dated change-log.md heading for {version}', file=sys.stderr)
        return f'<span class="version-badge">v{version}</span>'
    return f'<span class="version-badge" title="Released {m.group(1)}">v{version}</span>'


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

    counts = {
        'canonical': 0,
        'video_embed': 0,
        'color_swatch': 0,
        'code_punct': 0,
        'ext_sig': 0,
        'data_sig': 0,
        'md_default': 0,
        'version_badge': 0,
    }
    badge = version_badge()

    for page in sorted(DOCS.rglob('*.html')):
        rel = page.relative_to(DOCS)
        text = page.read_text(encoding='utf-8')
        original = text

        text, n = _VERSION_BADGE.subn(badge, text)
        counts['version_badge'] += n

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

        text, span_fixes = fix_code_spans(text, _CODE_SPAN)
        counts['code_punct'] += span_fixes

        if rel.as_posix() == 'reference/PartialsJinjaExtension.html' and EXT_SIG_HTML in text:
            text = text.replace(EXT_SIG_HTML, EXT_SIG_HTML_FIXED, 1)
            counts['ext_sig'] += 1

        if rel.parent.as_posix() == 'reference' and DATA_SIG_HTML in text:
            counts['data_sig'] += text.count(DATA_SIG_HTML)
            text = text.replace(DATA_SIG_HTML, DATA_SIG_HTML_FIXED)

        if rel.as_posix() == 'index.html':
            text = text.replace(
                'content="https://mkennedy.codes/docs/jinja-partials"',
                f'content="{BASE_URL}"',
            )
            text = text.replace('<title>Jinja Partials | Jinja Partials</title>', f'<title>{HOME_TITLE}</title>')
            text = text.replace('content="Jinja Partials | Jinja Partials"', f'content="{HOME_TITLE}"')

        if text != original:
            page.write_text(text, encoding='utf-8')

    for page in sorted((DOCS / 'reference').glob('*.md')):
        text = page.read_text(encoding='utf-8')
        original = text
        text, span_fixes = fix_code_spans(text, _MD_CODE_SPAN)
        counts['code_punct'] += span_fixes
        if page.name == 'PartialsJinjaExtension.md' and EXT_SIG_MD in text:
            text = text.replace(EXT_SIG_MD, EXT_SIG_MD_FIXED, 1)
            counts['ext_sig'] += 1
        if DATA_SIG_MD in text:
            counts['data_sig'] += text.count(DATA_SIG_MD)
            text = text.replace(DATA_SIG_MD, DATA_SIG_MD_FIXED)
        text, n = _MD_NESTED_DEFAULT.subn(r'`\1\2`', text)
        counts['md_default'] += n
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
        f'code spans unsmarted: {counts["code_punct"]}, '
        f'extension signatures: {counts["ext_sig"]}, '
        f'**data signatures: {counts["data_sig"]}, '
        f'md nested defaults: {counts["md_default"]}, '
        f'search.json skill->skills: {skill_fixes}, '
        f'version badges ({badge}): {counts["version_badge"]}'
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

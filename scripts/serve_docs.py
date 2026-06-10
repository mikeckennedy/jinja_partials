#!/usr/bin/env python3
"""Serve the committed docs/ under /docs/jinja-partials for a faithful production-layout preview."""

from __future__ import annotations

import functools
import http.server
import socketserver
from pathlib import Path

PREFIX = '/docs/jinja-partials'
PORT = 8099
ROOT = Path(__file__).resolve().parent.parent / 'docs'


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        clean = path.split('?', 1)[0].split('#', 1)[0]
        if clean.startswith(PREFIX):
            path = clean[len(PREFIX) :] or '/'
        return super().translate_path(path)

    def send_head(self):
        if self.path in ('/', PREFIX):
            self.send_response(302)
            self.send_header('Location', PREFIX + '/')
            self.end_headers()
            return None
        return super().send_head()


class Server(socketserver.TCPServer):
    allow_reuse_address = True


def main():
    if not ROOT.is_dir():
        raise SystemExit(f'Run build_docs.py first; {ROOT} missing')
    with Server(('127.0.0.1', PORT), functools.partial(Handler, directory=str(ROOT))) as httpd:
        print(f'-> http://127.0.0.1:{PORT}{PREFIX}/  (Ctrl+C to stop)')
        httpd.serve_forever()


if __name__ == '__main__':
    main()

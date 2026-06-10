#!/usr/bin/env python3
"""Quarto pre-render hook: undo heading demotion inside fenced code blocks.

Great Docs demotes README headings by one level ('#' -> '##') when generating
index.qmd, but it also applies this to '#' comment lines inside fenced code
blocks, corrupting Python examples. This rewrites '## ' back to '# ' on lines
inside code fences only. Stdlib only; idempotent.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

_DIR = Path(os.environ.get('QUARTO_PROJECT_DIR', '.')).resolve()
_FENCE = re.compile(r'^(`{3,}|~{3,})')
_DEMOTED = re.compile(r'^## (?!#)')


def fix_text(text: str) -> str:
    lines = text.splitlines(keepends=True)
    in_fence = False
    fence_marker = ''
    for i, line in enumerate(lines):
        m = _FENCE.match(line)
        if m:
            if not in_fence:
                in_fence = True
                fence_marker = m.group(1)[0] * len(m.group(1))
            elif line.startswith(fence_marker):
                in_fence = False
            continue
        if in_fence and _DEMOTED.match(line):
            lines[i] = '# ' + line[3:]
    return ''.join(lines)


def main() -> None:
    changed = 0
    for path in _DIR.glob('*.qmd'):
        text = path.read_text(encoding='utf-8')
        fixed = fix_text(text)
        if fixed != text:
            path.write_text(fixed, encoding='utf-8')
            changed += 1
    print(f'[fix_readme_code_comments] fixed {changed} file(s)')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Build the docs and mirror the static site into the committed repo-root docs/ folder.

The great-docs/ build directory is ephemeral (regenerated on every build and
self-gitignored), so the served site lives in docs/, which IS committed and
deployed by git push + git pull on the server.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPTS.parent  # pyproject.toml + great-docs.yml live at the git root
SITE = REPO_ROOT / 'great-docs' / '_site'
DEST = REPO_ROOT / 'docs'

# Agent-facing files that must exist in every build (see great-docs.yml `skill.file`)
REQUIRED_OUTPUTS = (
    'llms.txt',
    'llms-full.txt',
    'skill.md',
    '.well-known/agent-skills/index.json',
    '.well-known/agent-skills/jinja-partials/SKILL.md',
)
USER_GUIDE_MARKER = 'This is the User Guide documentation for the package.'


def main() -> int:
    # Prefer the great-docs entry point from the same venv as this interpreter.
    great_docs = Path(sys.executable).with_name('great-docs')
    cmd = [str(great_docs) if great_docs.exists() else 'great-docs', 'build']
    if subprocess.run(cmd, cwd=REPO_ROOT).returncode != 0:
        return 1

    if not SITE.is_dir():
        print(f'build output missing: {SITE}', file=sys.stderr)
        return 1

    # Great Docs reports success even when it silently skips the agent files (for
    # example when it cannot import the package for llms-full.txt), so check the
    # output before mirroring it into the committed site.
    missing = [name for name in REQUIRED_OUTPUTS if not (SITE / name).is_file()]
    if missing:
        print(f'build output incomplete, missing: {", ".join(missing)}', file=sys.stderr)
        return 1
    llms_full = (SITE / 'llms-full.txt').read_text(encoding='utf-8')
    if USER_GUIDE_MARKER not in llms_full:
        print(f'llms-full.txt has no user guide section ({USER_GUIDE_MARKER!r} missing)', file=sys.stderr)
        return 1

    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(SITE, DEST)
    file_count = sum(1 for p in DEST.rglob('*') if p.is_file())
    print(f'Mirrored -> {DEST} ({file_count} files)')

    return subprocess.run([sys.executable, str(_SCRIPTS / 'postprocess_site.py')]).returncode


if __name__ == '__main__':
    raise SystemExit(main())

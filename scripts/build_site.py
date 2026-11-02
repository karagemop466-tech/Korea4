#!/usr/bin/env python3
"""Build a clean Pages artifact, retaining old URLs as safe redirects.

Prior sessions' original pages and datasets stay in the repository unchanged for
historical research. They contained superseded free-time claims, so the deployed
artifact substitutes redirects rather than publishing those claims as fact.
"""
from __future__ import annotations
import html
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'


def legacy_destination(old: str) -> str:
    name = Path(old).name.lower()
    if name in {'index.html', 'flat-dashboard.html'}:
        return 'index.html'
    if 'vacation' in name or 'executive' in name:
        return 'site/planner/vacation.html'
    if 'flag' in name:
        return 'site/planner/review.html'
    if 'radio' in name:
        return 'site/planner/radio.html'
    if 'source' in name or 'method' in name:
        return 'site/planner/methodology.html'
    if 'mlb' in name:
        return 'site/planner/mlb.html'
    if 'nfl' in name:
        return 'site/planner/nfl.html'
    if 'ncaaf' in name:
        return 'site/planner/college.html'
    if 'westwood' in name:
        return 'site/planner/westwood.html'
    return 'site/planner/calendar.html'


def main():
    if OUT.resolve() != (ROOT / '_site').resolve():
        raise ValueError('Unsafe output location')
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / 'site/data').mkdir(parents=True)
    (OUT / 'site/assets').mkdir(parents=True)
    shutil.copy2(ROOT / 'index.html', OUT / 'index.html')
    shutil.copytree(ROOT / 'site/planner', OUT / 'site/planner')
    shutil.copy2(ROOT / 'site/data/events.json', OUT / 'site/data/events.json')
    shutil.copy2(ROOT / 'site/assets/outer-sunset.jpg', OUT / 'site/assets/outer-sunset.jpg')
    (OUT / '.nojekyll').write_text('')
    tracked = subprocess.check_output(['git', 'ls-files', '*.html'], cwd=ROOT, text=True).splitlines()
    count = 0
    for old in tracked:
        if old == 'index.html' or old.startswith('site/planner/'):
            continue
        destination = legacy_destination(old)
        redirect = os.path.relpath(OUT / destination, (OUT / old).parent).replace(os.sep, '/')
        p = OUT / old
        p.parent.mkdir(parents=True, exist_ok=True)
        link = html.escape(redirect, quote=True)
        p.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="0; url={link}"><meta name="robots" content="noindex"><title>Planner page moved</title></head><body><p>The previous page has been superseded by a source-linked planner with corrected uncertainty. <a href="{link}">Continue to the current page</a>.</p></body></html>\n''')
        count += 1
    print(f'Built {OUT.relative_to(ROOT)} with {count} legacy URL redirects')

if __name__ == '__main__':
    main()

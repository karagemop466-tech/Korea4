import os
import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / os.environ.get('TEST_SITE_DIR', '_site')

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for key in ('href', 'src'):
            if values.get(key):
                self.urls.append(values[key])
        if tag == 'meta' and values.get('http-equiv', '').lower() == 'refresh':
            match = re.search(r'url=(.*)$', values.get('content', ''), re.I)
            if match:
                self.urls.append(match.group(1))

class BuiltSiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if 'TEST_SITE_DIR' not in os.environ:
            subprocess.run(['python3', str(ROOT / 'scripts/build_site.py')], cwd=ROOT, check=True, capture_output=True, text=True)

    def test_all_static_local_links_exist(self):
        missing = []
        for page in SITE.rglob('*.html'):
            parser = Links()
            parser.feed(page.read_text())
            for url in parser.urls:
                parsed = urlsplit(url)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target = (page.parent / unquote(parsed.path)).resolve()
                if not target.is_file():
                    missing.append(f'{page.relative_to(SITE)} -> {url}')
        self.assertEqual(missing, [], '\n'.join(missing))

    def test_javascript_routes_and_assets_exist(self):
        app = (SITE / 'site/planner/app.js').read_text()
        paths = set(re.findall(r"path\('([^']+)'\)", app))
        missing = [p for p in paths if not (SITE / p.split('?', 1)[0]).is_file()]
        self.assertEqual(missing, [])
        self.assertTrue((SITE / 'site/data/events.json').is_file())
        self.assertTrue((SITE / 'site/assets/outer-sunset.jpg').is_file())
        self.assertTrue((SITE / 'site/planner/core.js').is_file())

    def test_legacy_urls_are_redirected_not_published_as_verified(self):
        for path in ('calendar.html', 'vacation.html', 'site/vacation.html', 'site/pages/vacation-windows.html', 'docs/index.html', 'docs/vacation.html'):
            text = (SITE / path).read_text()
            self.assertIn('superseded', text)
            self.assertIn('http-equiv="refresh"', text)
            self.assertNotIn('4-day Feb', text)

class LegacyRedirectSourcesTest(unittest.TestCase):
    def test_jekyll_redirects_cover_every_tracked_legacy_html(self):
        tracked = subprocess.check_output(['git', 'ls-files', '*.html'], cwd=ROOT, text=True).splitlines()
        expected = {p for p in tracked if p != 'index.html' and not p.startswith(('site/planner/', 'redirects/'))}
        redirects = {}
        for source in (ROOT / 'redirects').glob('*.html'):
            text = source.read_text()
            m = re.match(r'^---\npermalink: /([^\n]+)\n---\n', text)
            self.assertIsNotNone(m, source.name)
            self.assertNotIn(m.group(1), redirects, source.name)
            redirects[m.group(1)] = source
            self.assertIn('http-equiv="refresh"', text)
        self.assertEqual(set(redirects), expected)
        excluded = {line.strip()[2:] for line in (ROOT / '_config.yml').read_text().splitlines() if line.strip().startswith('- ')}
        unexcluded = [p for p in expected if not any(p == x or p.startswith(x + '/') for x in excluded)]
        self.assertEqual(unexcluded, [], 'Original pages must not override redirect destinations')

if __name__ == '__main__':
    unittest.main()

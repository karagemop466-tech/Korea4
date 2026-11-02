import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'

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
        for path in ('calendar.html', 'vacation.html', 'site/vacation.html', 'site/pages/vacation-windows.html'):
            text = (SITE / path).read_text()
            self.assertIn('superseded', text)
            self.assertIn('http-equiv="refresh"', text)
            self.assertNotIn('4-day Feb', text)

if __name__ == '__main__':
    unittest.main()

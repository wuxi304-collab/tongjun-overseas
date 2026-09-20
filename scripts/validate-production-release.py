from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import re
import sys
import json
import hashlib

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '_prod')


class Parser(HTMLParser):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.ids = []
        self.links = []
        self.assets = []
        self.robots = []
        self.canonicals = []

    def handle_starttag(self, tag, attrs):
        self._read(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._read(tag, attrs)

    def _read(self, tag, attrs):
        data = dict(attrs)
        if data.get('id'):
            self.ids.append(data['id'])
        if tag == 'meta' and (data.get('name') or '').lower() == 'robots':
            self.robots.append((data.get('content') or '').lower())
        if tag == 'link' and 'canonical' in (data.get('rel') or '').lower().split():
            self.canonicals.append(data.get('href') or '')
        href = data.get('href')
        if tag == 'a' and href:
            self.links.append(href)
        for key in ('src', 'poster', 'data-src'):
            if data.get(key):
                self.assets.append(data[key])
        if tag == 'link' and href and 'canonical' not in (data.get('rel') or '').lower().split():
            self.assets.append(href)


def fail(message):
    raise SystemExit('ERROR: ' + message)


def target_name_for(path, current, stems):
    if path in ('', '/'):
        return current if path == '' else 'index.html'
    leaf = path.strip('/').split('/')[-1]
    if leaf.endswith('.html'):
        leaf = leaf[:-5]
    return stems.get(leaf)


def main():
    if not ROOT.is_dir():
        fail(f'production static root missing: {ROOT}')

    forbidden_dirs = {'api', 'lib', 'scripts', 'ops', 'tests', '.sync', '.git', '.github'}
    forbidden_files = {'CNAME', 'package.json', 'vercel.json', 'R7_TEST.txt', 'MINIMAX_ENV.example'}
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in forbidden_dirs:
            fail(f'internal/server path leaked into production static output: {rel}')
        if len(rel.parts) == 1 and rel.name in forbidden_files:
            fail(f'build-only root file leaked into production static output: {rel.name}')

    robots_txt = (ROOT / 'robots.txt').read_text(encoding='utf-8') if (ROOT / 'robots.txt').is_file() else ''
    if not robots_txt:
        fail('production robots.txt missing')
    if re.search(r'^\s*Disallow:\s*/\s*$', robots_txt, flags=re.M):
        fail('production robots.txt blocks the entire site')

    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 production HTML pages, found {len(htmls)}')
    stems = {p.stem: p.name for p in htmls}
    stems['index'] = 'index.html'

    parsed = {}
    sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8') if (ROOT / 'sitemap.xml').is_file() else ''
    broken_assets = []
    broken_routes = []
    broken_anchors = []

    for page in htmls:
        text = page.read_text(encoding='utf-8')
        parser = Parser(page.name)
        parser.feed(text)
        parsed[page.name] = parser

        if len(parser.canonicals) != 1:
            fail(f'{page.name}: expected exactly one canonical, found {len(parser.canonicals)}')
        canonical = parser.canonicals[0]
        if not canonical.startswith('https://exoticalloycn.com') or '.html' in canonical:
            fail(f'{page.name}: production canonical invalid: {canonical}')

        if len(set(parser.ids)) != len(parser.ids):
            fail(f'{page.name}: duplicate id detected')

        if 'assets/site.js?v=20260916-r14-2' not in text:
            fail(f'{page.name}: R14.2 runtime cache version missing')
        if 'SINCE 2010' in text:
            fail(f'{page.name}: stale founding-year marker returned')

        robots = parser.robots[0] if parser.robots else ''
        route = '/' if page.name == 'index.html' else '/' + page.stem
        in_sitemap = f'<loc>https://exoticalloycn.com{route}</loc>' in sitemap
        if 'noindex' in robots and in_sitemap:
            fail(f'{page.name}: noindex page appears in sitemap')
        if 'noindex' not in robots and page.name != '404.html' and not in_sitemap:
            fail(f'{page.name}: indexable production page missing from sitemap')

    for page in htmls:
        parser = parsed[page.name]
        for value in parser.assets:
            u = urlsplit(value)
            if u.scheme in ('http', 'https', 'data') or value.startswith('//'):
                continue
            path = u.path
            if not path.startswith('/assets/') and not path.startswith('/manifest.webmanifest') and not path.startswith('/.well-known/'):
                continue
            rel = path.lstrip('/')
            if not (ROOT / rel).is_file():
                broken_assets.append((page.name, value))

        for href in parser.links:
            if href.startswith(('mailto:', 'tel:', 'javascript:', 'http://', 'https://', '#')):
                if href.startswith('#'):
                    frag = href[1:]
                    if frag and frag not in set(parser.ids):
                        broken_anchors.append((page.name, href, page.name, frag))
                continue
            u = urlsplit(href)
            target = target_name_for(u.path, page.name, stems)
            if not target:
                broken_routes.append((page.name, href))
                continue
            if u.fragment and u.fragment not in set(parsed[target].ids):
                broken_anchors.append((page.name, href, target, u.fragment))

    if broken_assets:
        fail(f'{len(broken_assets)} broken production asset reference(s): {broken_assets[:20]}')
    if broken_routes:
        fail(f'{len(broken_routes)} broken production route(s): {broken_routes[:20]}')
    if broken_anchors:
        fail(f'{len(broken_anchors)} broken production anchor(s): {broken_anchors[:20]}')

    release_path = ROOT / '.well-known' / 'release.json'
    if not release_path.is_file():
        fail('R15.14 production release identity missing')
    try:
        release = json.loads(release_path.read_text(encoding='utf-8'))
    except Exception as exc:
        fail(f'R15.14 production release identity is invalid JSON: {exc}')
    expected_release = {
        'service': 'tongjun-overseas',
        'site_release': 'V34.152 R15.14',
        'source_branch': 'feat/v34.152-r15.14-public-asset-hygiene',
        'visual_release': 'V34.152 R15.7',
        'environment': 'production',
        'canonical_origin': 'https://exoticalloycn.com',
        'release_identity_version': 1,
    }
    for key, expected in expected_release.items():
        if release.get(key) != expected:
            fail(f'R15.14 production release identity mismatch for {key}: {release.get(key)!r}')
    if not re.fullmatch(r'[0-9a-f]{40}', str(release.get('source_commit') or '')):
        fail('R15.14 production release source_commit must be a 40-character git SHA')
    visual_manifest = Path('VISUAL_MANIFEST_R15_7.json')
    if not visual_manifest.is_file():
        fail('R15.7 visual manifest source missing while validating release identity')
    expected_visual_sha = hashlib.sha256(visual_manifest.read_bytes()).hexdigest()
    if release.get('visual_manifest_sha256') != expected_visual_sha:
        fail('R15.14 production release visual manifest SHA256 mismatch')

    required = [
        ROOT / 'assets' / 'site.js',
        ROOT / 'assets' / 'brand-v34.152-r14.css',
        ROOT / 'assets' / 'tongjun-logo.svg',
        ROOT / '.well-known' / 'security.txt',
        ROOT / 'manifest.webmanifest',
        ROOT / 'sitemap.xml',
        ROOT / 'llms.txt',
    ]
    for path in required:
        if not path.is_file():
            fail(f'required production static file missing: {path.relative_to(ROOT)}')

    print(
        'PASS: R15 production static release — 50 pages, canonical/indexing consistency, '
        '0 internal leaks, 0 broken assets/routes/anchors, R15.14 release identity and current RFQ runtime active.'
    )


if __name__ == '__main__':
    main()

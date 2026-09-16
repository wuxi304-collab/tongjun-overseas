from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
BASE = '/tongjun-overseas/'


class PageParser(HTMLParser):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.ids = []
        self.links = []
        self.assets = []
        self.robots = []

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
        href = data.get('href')
        if tag == 'a' and href:
            if urlsplit(href).path.startswith(BASE + 'assets/'):
                self.assets.append(href)
            else:
                self.links.append(href)
        for key in ('src', 'poster', 'data-src'):
            if data.get(key):
                self.assets.append(data[key])
        if tag == 'link' and href:
            self.assets.append(href)


def fail(message):
    raise SystemExit('ERROR: ' + message)


def main():
    if not ROOT.is_dir():
        fail(f'Pages root missing: {ROOT}')

    forbidden_dirs = {'ops', 'api', 'scripts', 'tests', '.git', '.github', '.sync'}
    leaked = []
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in forbidden_dirs:
            leaked.append(str(rel))
    if leaked:
        fail(f'internal/server paths leaked into Pages artifact: {leaked[:20]}')
    if (ROOT / 'CNAME').exists():
        fail('CNAME must not ship in the temporary Pages mirror')

    robots_txt = (ROOT / 'robots.txt').read_text(encoding='utf-8') if (ROOT / 'robots.txt').is_file() else ''
    if robots_txt.strip() != 'User-agent: *\nDisallow: /':
        fail('Pages robots.txt must disallow the temporary mirror')

    htmls = sorted(ROOT.glob('*.html'))
    if len(htmls) != 50:
        fail(f'expected 50 root HTML pages, found {len(htmls)}')

    parsed = {}
    duplicate_ids = []
    for page in htmls:
        text = page.read_text(encoding='utf-8')
        if '"/tongjun-overseas/>' in text or "'/tongjun-overseas/>" in text:
            fail(f'malformed BASE_PATH rewrite in {page.name}')
        parser = PageParser(page.name)
        parser.feed(text)
        parsed[page.name] = parser
        if len(parser.robots) != 1 or 'noindex' not in parser.robots[0] or 'nofollow' not in parser.robots[0]:
            fail(f'Pages noindex/nofollow marker missing or duplicated in {page.name}')
        seen = set()
        for ident in parser.ids:
            if ident in seen:
                duplicate_ids.append((page.name, ident))
            seen.add(ident)
    if duplicate_ids:
        fail(f'duplicate ids found: {duplicate_ids[:20]}')

    core = ['index.html', 'technical-data.html', 'quality.html', 'rfq.html', 'materials.html', 'product-forms.html', 'about.html', 'resources.html', 'industries.html']
    for name in core:
        text = (ROOT / name).read_text(encoding='utf-8')
        if 'brand-v34.152-r14.css?v=20260916-r14-1' not in text:
            fail(f'R14.1 stylesheet missing in {name}')
        if 'assets/site.js?v=20260916-r14-2' not in text:
            fail(f'R14.2 site.js cache version missing in {name}')

    tech = (ROOT / 'technical-data.html').read_text(encoding='utf-8')
    quality = (ROOT / 'quality.html').read_text(encoding='utf-8')
    rfq = (ROOT / 'rfq.html').read_text(encoding='utf-8')
    route = (ROOT / 'supply-route.html').read_text(encoding='utf-8')
    problem = (ROOT / 'problem-order.html').read_text(encoding='utf-8')
    industries = (ROOT / 'industries.html').read_text(encoding='utf-8')

    if 'Technical data for sourcing decisions.' not in tech:
        fail('Technical Data headline regressed')
    for name, text in [('technical-data.html', tech), ('quality.html', quality), ('rfq.html', rfq)]:
        if text.count('class="r14-action-rail"') != 1:
            fail(f'R14 action rail count wrong in {name}')
    if 'href="#rfqForm"' not in rfq:
        fail('RFQ direct form jump missing')
    for marker in (
        'class="r14-rfq-fast-note"',
        'class="field full r14-rfq-optional"',
        'class="field full r14-rfq-advanced"',
    ):
        if rfq.count(marker) != 1:
            fail(f'RFQ progressive disclosure marker count wrong: {marker}')
    if rfq.find('05 · Application / notes') > rfq.find('Optional qualification + logistics'):
        fail('required Application block must precede optional qualification/logistics')
    for marker, text in (
        ('id="rfq-name"', rfq), ('for="rfq-name"', rfq),
        ('id="route-family"', route), ('for="route-family"', route),
        ('id="problem-family"', problem), ('for="problem-family"', problem),
    ):
        if marker not in text:
            fail(f'buyer-form semantic marker missing: {marker}')
    for anchor in ('id="energy"', 'id="marine"'):
        if anchor not in industries:
            fail(f'Industries deep-link destination missing: {anchor}')

    runtime = (ROOT / 'assets' / 'site.js').read_text(encoding='utf-8')
    for marker in (
        'Product Context:',
        'First Seen:',
        'routeError.requestId=safe(result.request_id,80)',
        'Secure Route Attempt:',
        "setStore('tj_last_rfq','email_fallback')",
        'use Copy Structured RFQ if no mail app opens.',
        "fetch('/tongjun-overseas/api/rfq'",
    ):
        if marker not in runtime:
            fail(f'R14.2 RFQ runtime marker missing: {marker}')

    css = (ROOT / 'assets' / 'brand-v34.152-r14.css').read_text(encoding='utf-8')
    for marker in (
        'V34.152 R14.1',
        'body.brand-v34[data-page="technical-data"] .visual-band{display:none!important}',
        'body.brand-v34[data-page="rfq"] .visual-band{display:none!important}',
        'body.brand-v34[data-page="rfq"] #rfqForm{order:1!important',
        'body.brand-v34[data-page="home"] .hero-positioning{display:none!important}',
        'body.brand-v34[data-page="rfq"] .r14-rfq-optional-grid',
        '.formgrid>.field.full:has(#rfqReadiness)',
        'body.brand-v34 #energy',
        'body.brand-v34 #marine',
    ):
        if marker not in css:
            fail(f'missing R14.1 CSS gate: {marker}')

    forbidden_markers = (
        'SINCE 2010', 'TONGJUN SPECIAL METALS', 'hero-special-metals.webp', 'supply-route.webp',
        'quality-lab-r13', 'engineering-team-r13', 'technical-lab-r13', 'logo-r13.avif', 'hero-port-r13.avif',
        'tj-logo-r13', 'tj-wordmark',
    )
    stem_to_name = {p.stem: p.name for p in htmls}
    stem_to_name['index'] = 'index.html'
    broken_assets = []
    broken_routes = []
    broken_anchors = []

    for page in htmls:
        text = page.read_text(encoding='utf-8')
        for marker in forbidden_markers:
            if marker in text:
                fail(f'forbidden marker {marker!r} in {page.name}')
        parser = parsed[page.name]
        for value in parser.assets:
            path = urlsplit(value).path
            if not path.startswith(BASE + 'assets/'):
                continue
            rel = path[len(BASE):]
            if not (ROOT / rel).is_file():
                broken_assets.append((page.name, value))

        for href in parser.links:
            if href.startswith(('mailto:', 'tel:', 'javascript:', 'http://', 'https://')):
                continue
            u = urlsplit(href)
            path = u.path
            if path == '':
                target_name = page.name
            else:
                if path.startswith(BASE):
                    path = path[len(BASE)-1:]
                if path in ('', '/'):
                    target_name = 'index.html'
                else:
                    target = path.strip('/').split('/')[-1]
                    if target.endswith('.html'):
                        target = target[:-5]
                    target_name = stem_to_name.get(target)
                    if not target_name:
                        broken_routes.append((page.name, href))
                        continue
            if u.fragment and u.fragment not in set(parsed[target_name].ids):
                broken_anchors.append((page.name, href, target_name, u.fragment))

    if broken_assets:
        fail(f'{len(broken_assets)} broken local asset reference(s): {broken_assets[:20]}')
    if broken_routes:
        fail(f'{len(broken_routes)} broken internal route(s): {broken_routes[:20]}')
    if broken_anchors:
        fail(f'{len(broken_anchors)} broken internal deep-link anchor(s): {broken_anchors[:20]}')

    print(
        'PASS: R15 Pages release — 50 root pages, temporary mirror noindex, internal paths excluded, '
        'RFQ trace runtime gated, 0 broken assets/routes/anchors and 0 duplicate ids.'
    )


if __name__ == '__main__':
    main()
